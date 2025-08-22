from dataclasses import dataclass
from typing import Dict, List, Tuple

from log import CustomLogger
from numpy import float64
from scipy.stats import binomtest

from drive.network.factory import factory_register
from drive.network.models import Data_Interface, Network_Interface

logger = CustomLogger.get_logger(__name__)


@dataclass
class Pvalues:
    """Class that is responsible for determining the pvalues for each network"""

    name: str = "Pvalue plugin"

    @staticmethod
    def _determine_pvalue(
        phenotype: str,
        phenotype_percent: float,
        carriers_count: int,
        network_size: int,
    ) -> float64:
        """Function that will determine the pvalue for each network

        Parameters
        ----------
        phenotype : str
            id for the phenotype

        phenotype_percent : float
            float that tells what the prevalence of the phenotype in the
            cohort population is

        carriers_count : int
            number of carriers in the network

        network_size : int
            size of the network

        Returns
        -------
        float
            Returns the calculated pvalue
        """
        # the probability is 1 if the carrier count is zero because it is chances of
        # finding 0 or higher which is everyone
        if carriers_count == 0:
            logger.debug(f"carrier count = 0 therefore pvalue for {phenotype} = 1")
            return 1
        elif carriers_count - 1 == 0:
            logger.debug(
                "When the proband was removed, there were no more carriers who remained in the network. Therefore returning a p-value of 1"
            )
            return 1

        result = binomtest(carriers_count - 1, network_size - 1, phenotype_percent)

        pvalue = result.pvalue

        logger.debug(f"pvalue for {phenotype} = {pvalue}")

        return pvalue

    @staticmethod
    def _determine_phenotype_frequency(
        phecode: str, phenotype_counts: Dict[str, List[str]]
    ) -> float:
        """calculate the phenotype frequency in the cohort

        Parameters
        ----------
        phecode : str
            phecode id. This value will only be used for a logging statement

        phenotype_counts : Dict[str, List[str]]
            Dictionary that has list for individuals who are
            cases, controls, or exclusions.

        Returns
        -------
        float
            returns the phenotype frequency as a float
        """

        # We need to first check if there are even controls in the file
        phenotype_frequency = len(phenotype_counts.get("cases")) / (
            len(phenotype_counts.get("controls")) + len(phenotype_counts.get("cases"))
        )

        # logger.verbose(
        #     f"For PheCode, {phecode}, {len(phenotype_counts.get('cases'))} cases and {len(phenotype_counts.get('controls'))} were identified giving a phenotype frequency of {phenotype_frequency}"  # noqa: E501
        # )

        return phenotype_frequency

    @staticmethod
    def _get_carrier_count_in_network(
        phenotype_counts: Dict[str, List[str]], network: Network_Interface
    ) -> int:
        """Determine the number of individual cases that are
        also in the network

        Parameters
        ----------
        phenotype_counts : Dict[str, List[str]]
            Dictionary that has list for individuals who are
            cases, controls, or exclusions.

        network : Network_Interface
            Network object with information about members of
            the networks and what haplotypes are in the network

        Returns
        -------
        int
            returns the number of carriers in the network
        """
        # determine the number of carriers in the network

        return len(network.members.intersection(phenotype_counts.get("cases")))

    @staticmethod
    def _get_carriers_in_network(
        phenotype_counts: Dict[str, List[str]], network: Network_Interface
    ) -> str:
        """Generate a set of cases that are in the network

        Parameters
        ----------
        phenotype_counts : Dict[str, List[str]]
            Dictionary that has list for individuals who are
            cases, controls, or exclusions.

        network : Network_Interface
            Network object with information about members of
            the networks and what haplotypes are in the network

        Returns
        -------
        str
            returns a string of individuals that are in both the phenotype_counts
            case set and the network members set. If this interection is empty
            then it returns a str "N/A"
        """
        # determine the number of carriers in the network
        case_individuals = network.members.intersection(phenotype_counts.get("cases"))

        if case_individuals:
            return ", ".join(
                network.members.intersection(phenotype_counts.get("cases"))
            )  # noqa: E501
        else:
            return "N/A"

    @staticmethod
    def _get_exclusions_in_network(
        phenotype_counts: Dict[str, List[str]], network: Network_Interface
    ) -> str:
        """Generate a set of cases that are in the network

        Parameters
        ----------
        phenotype_counts : Dict[str, List[str]]
            Dictionary that has list for individuals who are
            cases, controls, or exclusions.

        network : Network_Interface
            Network object with information about members of
            the networks and what haplotypes are in the network

        Returns
        -------
        str
            returns a string of individuals that are in both the phenotype_counts
            exclusion set and the network members set. If this interection is
            empty then it returns a str "N/A"
        """
        # determine the number of carriers in the network
        excluded_individuals = network.members.intersection(
            phenotype_counts.get("excluded")
        )  # noqa: E501

        if excluded_individuals:
            return ", ".join(
                network.members.intersection(phenotype_counts.get("excluded"))
            )  # noqa: E501
        else:
            "N/A"

    def _remove_exclusions(
        phenotype_counts: Dict[str, List[str]], network: Network_Interface
    ) -> Tuple[int, int]:
        """determine size of network after removing excluded
        individuals

        Parameters
        ----------
        phenotype_counts : Dict[str, List[str]]
            Dictionary that has list for individuals who are
            cases, controls, or exclusions.

        network : Network_Interface
            Network object with information about members of
            the networks and what haplotypes are in the network

        Returns
        -------
        Tuple[int, int]
            returns the number of individuals in the network,
            not counting those individuals classified as
            excluded in the phenotype_counts dictionary. Also
            returns the number of individuals excluded. Also returns the
        """

        return (
            len(network.members.difference(phenotype_counts.get("excluded"))),
            len(network.members.intersection(phenotype_counts.get("excluded"))),
        )

    def _gather_network_information(
        self,
        network: Network_Interface,
        cohort_carriers: Dict[str, Dict[str, List[str]]],
    ) -> tuple[str, str, Dict[str, str]]:
        """Determine information about how many
        carriers are in each network, the percentage, the IIDs of
        the carriers in the network, and use this to calculate the
        pvalue for the network. The function keeps track of the
        smallest non-zero pvalue and returns it or NA

        Parameters
        ----------

        network : Network
            Network object attributes for iids, pairs, and haplotypes

        cohort_carriers : Dict[str, Dict[str, List[str]]]
            dictionary where the keys are phenotype ids and the values are a dictionary
            with the list of cases/controls/exclusions

        Returns
        -------
        Tuple[str, str, Dict[str, str]]
            returns a tuple where the first element is the string of the
            minimum phenotype code. The second value is the description
            of the minimum phenotype. The third value is a dictionary
            that for each phenotype has a string with the number of
            cases, number of excluded individuals, and the p-values.
        """
        # setting null values for the output string and the cur_min_phecode string.
        # Also setting a value of 1 for the cur_min_pvalue because this will be the
        # largest pvalue possible

        cur_min_pvalue = 1

        cur_min_phenotype = ""

        phenotype_pvalues = {}

        # iterating over each phenotype
        for phenotype, phenotype_counts in cohort_carriers.items():
            # if there are no controls then we can't do the
            # stats and should just return a string of N/A for all values
            if len(phenotype_counts.get("controls")) == 0:
                phenotype_pvalues[phenotype] = "N/A\tN/A\tN/A\tN/A"
            else:
                phenotype_freq = Pvalues._determine_phenotype_frequency(
                    phenotype, phenotype_counts
                )

                num_carriers_in_network = Pvalues._get_carrier_count_in_network(
                    phenotype_counts, network
                )

                carrier_str = Pvalues._get_carriers_in_network(
                    phenotype_counts, network
                )

                exclusion_str = Pvalues._get_exclusions_in_network(
                    phenotype_counts, network
                )

                (
                    network_size_after_exclusions,
                    excluded_count,
                ) = Pvalues._remove_exclusions(phenotype_counts, network)

                # calling the sub function that determines the pvalue
                pvalue: float = Pvalues._determine_pvalue(
                    phenotype,
                    phenotype_freq,
                    num_carriers_in_network,
                    network_size_after_exclusions,
                )

                # Next two lines create the string and then concats it to the output_str

                phenotype_str = f"{num_carriers_in_network}\t{carrier_str}\t{excluded_count}\t{exclusion_str}\t{pvalue}"  # noqa: E501

                phenotype_pvalues[phenotype] = phenotype_str

                # Now we will see if the phecode is lower then the cur_min_pvalue.
                # If it is then we will change the cur_min_pvalue and we will
                # update the cur_min_phecode
                if pvalue < cur_min_pvalue and pvalue != 0:
                    cur_min_pvalue = pvalue

                    cur_min_phenotype = phenotype

        # if a minimum phecode is identified then we need to create a string, otherwise
        # we use N/A's
        if not cur_min_phenotype:
            cur_min_phenotype = "N/A"
            cur_min_pvalue = "N/A"

        # return the pvalue_output string first and either a tuple of N/As or the min
        # pvalue/min_phecode
        return cur_min_pvalue, cur_min_phenotype, phenotype_pvalues

    @staticmethod
    def _get_descriptions(
        phecode_description: dict[str, dict[str, str]], min_phecode: str
    ) -> str:
        """Method to get the description for the minimum phecode
        Parameters
        ----------
        phecode_descriptions : dict[str, dict[str, str]]
            dictionary with descriptions of each phecode. The outer key is the
            phenotype id. The inner key is the string phenotype and the value is a
            string that describes the phenotype

        min_phecode : str
            minimum phecode string

        Returns
        -------
        str
            returns a string that has the phecode description
        """
        # getting the description
        desc_dict = phecode_description.get(min_phecode, {})

        # getting the phenotype string if key exists,
        # otherwise returns an empty string
        logger.debug(f"description_str = {desc_dict.get('phenotype', 'N/A')}")

        return desc_dict.get("phenotype", "N/A")

    def analyze(self, **kwargs) -> None:
        # this is the DataHolder model. We will use the networks, the
        # affected_inds, and the phenotype_prevalances attribute
        data: Data_Interface = kwargs["data"]

        if data.carriers:
            for network in data.networks:
                # Determining the pvalues for the network
                (
                    min_pvalue_str,
                    min_phenotype_code,
                    phenotype_pvalues,
                ) = self._gather_network_information(network, data.carriers)

                min_phecode_description = self._get_descriptions(
                    data.phenotype_descriptions, min_phenotype_code
                )

                # create an attribute that has all the strings for what is the
                # min_pvalue, the min_phenotype_code, and the description of the
                # phenotype
                network.min_pvalue_str = (
                    f"{min_pvalue_str}\t{min_phenotype_code}\t{min_phecode_description}"
                )

                # adding the dictionary of phenotype values to the attribute
                # pvalues
                network.pvalues = phenotype_pvalues


def initialize() -> None:
    factory_register("pvalues", Pvalues)
