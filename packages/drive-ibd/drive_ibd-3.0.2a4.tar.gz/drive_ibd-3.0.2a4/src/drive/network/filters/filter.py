import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, TypeVar

import numpy as np
from log import CustomLogger
from pandas import DataFrame, concat, read_csv

from drive.network.models import FileIndices, Genes

logger = CustomLogger.get_logger(__name__)

# we are going to create two exception class for the vertex

T = TypeVar("T", bound="IbdFilter")


@dataclass
class IbdFilter:
    """
    class handling the filtering of the IBD files provided

    Parameters
    ----------
    ibd_file : iterator[DataFrame]
        pandas dataframe being read in chunk by chunk. This data represents
        the pairwise IBD segments from hap-IBD, GERMLINE, RaPID, or iLASH

    indices : FileIndices
        object that abstracts away the indices needed based on the IBD program
        used

    target_gene : Genes
        namedTuple that has fields for the chromosome and the start and end
        region of the target locus

    filter : Optional[Callable] = None
        Function that will be used to filter the provided segments. Default
        functions will either filter to segments containing the target locus
        or those that overlap

    ibd_vs : DataFrame
        dataframe representing all the potential vertices in the graph. Each
        vertex is a haplotype

    ibd_pd : DataFrame
        dataframe representing the pairwise segments. Each row is the pair ids
        and the length of the segment

    hapid_map : Dict[str, int]
        dictionary mapping the haplotype to a unique integer id

    all_haplotypes : List[str]
        list of all the different haplotypes in the IBD data

    haplotype_id : int = 0
        This value is used as the counter and is incremented as the program runs

    """

    ibd_file: Iterator[
        DataFrame
    ]  # IBD segments being read in by chunks making the pandas dataframe an iterator
    indices: FileIndices
    target_gene: Genes
    filter: Optional[Callable] = None
    ibd_vs: DataFrame = field(default_factory=DataFrame)
    ibd_pd: DataFrame = field(default_factory=DataFrame)
    hapid_map: Dict[str, int] = field(default_factory=dict)
    all_haplotypes: List[str] = field(default_factory=list)
    haplotype_id: int = 0

    @classmethod
    def load_file(
        cls,
        ibd_file: Path,
        indices: FileIndices,
        target_gene: Genes,
        chunksize: int = 100_000,
    ) -> T:
        """Factory method that returns the IBDFilter model
        This method makes sure that the ibd file exists

        Parameters
        ----------
        ibd_file : Path
            Path object containing the filepath for the ibd
            file from hapibd, iLASH, etc...

        indices: FileIndices
            Object that has all the indices for the necessary
            columns in the ibd file. This object also has a
            get_haplotype_ids method that will form the
            haplotype ibd.

        target_gene : Genes
            namedtuple that has attributes for the
            chromosome, the gene start position, and the
            gene end position.

        chunksize : int
            number of rows of the dataframe to read in a 1 time.
            Larger chunksize will mean the data is loaded faster
            but memory also increases.

        Returns
        -------
        IbdFilter
            returns an initialized IbdFilter object

        Raises
        ------
        FileNotFoundError
            raises an error if the file doesn't exist
        """
        logger.verbose(f"Reading in the ibd input file at {ibd_file}")

        if not ibd_file.is_file():
            raise FileNotFoundError(f"The file, {ibd_file}, was not found")

        # we can set column types
        col_dtypes = {
            indices.id1_indx: "string[pyarrow]",
            indices.id2_indx: "string[pyarrow]",
            indices.str_indx: "int32",
            indices.end_indx: "int32",
            indices.cM_indx: "float32",
        }
        # we need to make sure that the id columns read in as strings no matter what
        input_file_chunks = read_csv(
            ibd_file,
            sep="\t",
            header=None,
            chunksize=chunksize,
            dtype=col_dtypes,
            engine="c",
        )

        return cls(input_file_chunks, indices, target_gene)

    def _generate_map(self, chunk_data: DataFrame) -> None:
        """Method that will generate the dictionary that maps hapibd to integers

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is determined by the
            chunksize argument to pd.read_csv. This value is currently set to 100,000.
        """
        haplotypes = chunk_data.values.ravel()

        logger.verbose(f"identified {len(haplotypes)} haplotypes in this chunk.")

        # iterate over each haplotype and add it to the
        # dictionary if the value is not present
        for value in haplotypes:
            key_value = self.hapid_map.setdefault(value, self.haplotype_id)
            if key_value == self.haplotype_id:
                self.haplotype_id += 1

    def _map_grids(self, data_chunk: DataFrame) -> None:
        """Function responsible for creating two new columns that
        have the haplotype id numbers.

        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.
        """
        # we are going to map the haplotype id to integers in a new
        # column. this needs to be done for both hapid1 an hapid2
        data_chunk.loc[:, "idnum1"] = data_chunk["hapid1"].map(self.hapid_map)

        data_chunk.loc[:, "idnum2"] = data_chunk["hapid2"].map(self.hapid_map)

    def _contains_filter(self, data_chunk: DataFrame, min_cm: int) -> DataFrame:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501
        # We are going to filter the data and then make a copy
        # of it to return so that we don't get the
        # SettingWithCopyWarning

        return data_chunk[
            (data_chunk[self.indices.str_indx] <= self.target_gene.start)
            & (data_chunk[self.indices.end_indx] >= self.target_gene.end)
            & (data_chunk[self.indices.cM_indx] >= min_cm)
        ].copy()

    def _overlaps_filter(self, data_chunk: DataFrame, min_cm: int) -> DataFrame:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501

        # We are going to filter the data and then make a copy
        # of it to return so that we don't get the
        # SettingWithCopyWarning
        return data_chunk[
            (
                (
                    (data_chunk[self.indices.str_indx] <= int(self.target_gene.start))
                    & (data_chunk[self.indices.end_indx] >= int(self.target_gene.start))
                )
                | (
                    (data_chunk[self.indices.str_indx] >= int(self.target_gene.start))
                    & (data_chunk[self.indices.end_indx] <= int(self.target_gene.end))
                )
                | (
                    (data_chunk[self.indices.str_indx] <= int(self.target_gene.end))
                    & (data_chunk[self.indices.end_indx] >= int(self.target_gene.end))
                )
            )
            & (data_chunk[self.indices.cM_indx] >= min_cm)
        ].copy()

    def set_filter(self, filter_option: str) -> None:
        """Method to determine how the user wishes to filter the IBD segments file

        Parameters
        ----------
        filter_option : str
            string that represents the user's choice for how to filter the ibd segments.
            If the user chooses 'contains' the only segments that contain the entire
            region are kept. If the user chooses 'overlaps' then segments that overlap
            at all with the target region are kept.
        """

        if filter_option == "contains":
            logger.info("Identifying IBD segments that contain the target region")
            self.filter = self._contains_filter
        elif filter_option == "overlaps":
            logger.info("Identifying IBD segments that overlap the target region")
            self.filter = self._overlaps_filter
        else:
            logger.critical(
                "Non-recognized filter option selected. Allowed values are 'contains' and 'overlaps'. Exiting program now..."  # noqa: E501
            )
            sys.exit(0)

    def _remove_dups(self, data: DataFrame) -> DataFrame:
        """Filters out rows where the haplotype ids are the
        same

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        Returns
        -------
        DataFrame
            returns a dataframe where we make sure that hapibd1 does != hapibd2

        Raises
        ------
        KeyError
            raises a key error if hapid1 or hapid2 are not columns in the dataframe
        """
        try:
            return data[data["hapid1"] != data["hapid2"]]
        except KeyError as e:
            logger.critical(
                f"Expected the keys hapid1 and hapid2 to be in the dataframe. Instead the only keys were: {', '.join(data.columns)}"  # noqa: E501
            )
            raise e(
                f"Expected the keys hapid1 and hapid2 to be in the dataframe. Instead the only keys were: {', '.join(data.columns)}"  # noqa: E501
            )

    def _generate_vertices(self, data_chunk: DataFrame) -> None:
        """Method that will generate the vertices dataframe which just has the
        columns idnum, hapID, and IID

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.
        """
        id1_df = data_chunk[["idnum1", "hapid1", self.indices.id1_indx]].rename(
            columns={"idnum1": "idnum", "hapid1": "hapID", 0: "IID"}
        )

        self.ibd_vs = concat([self.ibd_vs, id1_df])

        id2_df = data_chunk[["idnum2", "hapid2", self.indices.id2_indx]].rename(
            columns={"idnum2": "idnum", "hapid2": "hapID", 2: "IID"}
        )

        self.ibd_vs = concat([self.ibd_vs, id2_df])

    def _filter_for_cohort(
        self, chunk: DataFrame, cohort_ids: Optional[List[str]] = None
    ) -> DataFrame:
        """filter cohort chunk to individuals in the cohort
        list

        Parameters
        ----------
        chunk : DataFrame
            chunk of pandas dataframe that has information about the shared
            pairwise IBD segment.

        cohort_ids : List[str]
            Lists of ids that make up the cohort. The ibd_file will be filtered to only this list.

        Returns
        -------
        DataFrame
            returns the filtered pandas dataframe
        """  # noqa: E501
        # if no cohort ids were provided then we just return the chunk, otherwise we
        # filter the dataframe for where id1 and id2 are in the cohort
        if not cohort_ids:
            return chunk
        else:
            return chunk[
                (chunk[self.indices.id1_indx].isin(cohort_ids))
                & (chunk[self.indices.id2_indx].isin(cohort_ids))
            ]

    def _check_for_no_shared_segments(ibd_pd: DataFrame, ibd_vs: DataFrame) -> None:
        """Check to ensure that there were shared IBD segments
        found based on the input conditions

        Parameters
        ----------
        ibd_pd : DataFrame
            dataframe that has all the pairwise shared
            segments that satisfy the input conditions

        ibd_vs : DataFrame
            dataframe that has the information about each
            haplotype and individual that are in ibd_pd

        Raises
        ------
        ValueError
            raises a ValueError if the dataframes are empty
            because they cannot be empty or other steps of the
            program will fail.
        """
        if ibd_pd.empty:
            logger.critical(
                "There were no shared IBD segments that satisfied the provided input conditions"  # noqa: E501
            )
            raise ValueError(
                "There were no shared IBD segments that satisfied the provided input conditions. Please check to make sure that there is no typo in the target region or that the correct ibd input file was provided."  # noqa: E501
            )
        elif ibd_vs.empty:
            logger.critical(
                "There were no haplotype ids identified in the filtering step."
            )
            raise ValueError(
                "There were no haplotype ids identified in the filtering step."
            )
        else:
            logger.debug(
                f"Identified {ibd_pd.shape[0]} shared ibd segments with {ibd_vs.shape[0]} unique haplotypes"  # noqa: E501
            )

    def _check_empty_dataframes(self) -> None:
        """Check if the provided dataframe is empty. If it is
        then it raises an error and exits the program"""
        if self.ibd_pd.empty:
            logger.info(
                "No individuals from the analysis cohort share an IBD segment across the provided target region. Please ensure that the target region is correct. Exiting program now."  # noqa: E501
            )
            sys.exit(0)

    def preprocess(
        self,
        min_centimorgan: int,
        cohort_ids: Optional[List[str]] = None,
    ) -> None:
        """Method that will filter the ibd file.

        Parameters
        ----------
        min_centimorgan : int
            Minimum segment threshold that is used to filter
            the ibd file. Program only keeps segments that
            are greater than or equal to the threshold.

        cohort_ids : List[str]
            Lists of ids that make up the cohort. The ibd_file
            will be filtered to only this list.
        """
        # getting the start time for when the program begines to read in the ibd file
        start_time = datetime.now()

        for chunk in self.ibd_file:
            cohort_restricted_chunk = self._filter_for_cohort(chunk, cohort_ids)

            logger.debug(
                f"Identified {cohort_restricted_chunk.shape[0]} pairs in this chunk"
            )  # noqa: E501

            if cohort_restricted_chunk.empty:
                continue

            size_filtered_chunk = self.filter(cohort_restricted_chunk, min_centimorgan)

            logger.debug(
                f"{size_filtered_chunk.shape[0]} pairs remaining after filtering for the loci of interest with a {min_centimorgan} minimum shared segment threshold"  # noqa: E501
            )

            if not size_filtered_chunk.empty:
                # We have to add two column with the haplotype ids
                self.indices.get_haplotype_id(
                    size_filtered_chunk,
                    self.indices.id1_indx,
                    self.indices.hap1_indx,
                    "hapid1",
                )

                self.indices.get_haplotype_id(
                    size_filtered_chunk,
                    self.indices.id2_indx,
                    self.indices.hap2_indx,
                    "hapid2",
                )
                # We then need to make sure that there are no
                # duplicates in the dataframe
                removed_dups = self._remove_dups(size_filtered_chunk)

                # We need to update the mappings for the grids
                self._generate_map(removed_dups[["hapid1", "hapid2"]])

                self._map_grids(removed_dups)
                # concat the filtered dataframe with the ibd_pd
                # attribute to get all the edges in the graph
                self.ibd_pd = concat([self.ibd_pd, removed_dups])

                self._generate_vertices(removed_dups)

        self._check_empty_dataframes()

        self.ibd_pd.reset_index(drop=True, inplace=True)

        ids_in_ibd_pd = len(
            np.unique(
                np.concatenate(
                    [
                        self.ibd_pd[self.indices.id1_indx].unique(),
                        self.ibd_pd[self.indices.id2_indx].unique(),
                    ]
                )
            )
        )

        if len(cohort_ids) != 0:
            logger.info(
                f"{ids_in_ibd_pd} out of the {len(cohort_ids)} ids provided were found within the IBD data file after filtering"
            )
        else:
            logger.info(
                f"Identified {ids_in_ibd_pd} unique ids within the provided IBD data"
            )

        self.ibd_vs = self.ibd_vs.drop_duplicates().sort_values(by="idnum")

        # We are going to print out how long it took to read in the ibd file
        # if the user puts the program in verbose mod
        end_time = datetime.now()

        logger.verbose(
            f"Finished reading in the IBD file. Time spent reading file: {end_time - start_time}"
        )
