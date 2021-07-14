import enum
import random

from collections import namedtuple
from itertools import islice, starmap
from typing import Any, Dict, Generator, Iterator, List

from faker import Faker


class TableFormat(enum.Enum):
    COLUMN = 1
    ROW = 2


class Columns(enum.Enum):
    NAME = 1
    ADDRESS = 2
    PHONE_NUMBER = 3
    DATE_OF_BIRTH = 4
    JOB = 5
    BANK_ACCOUNT = 6
    SSN = 7


DEFAULT_COLUMNS = [
    Columns.NAME,
    Columns.ADDRESS,
    Columns.PHONE_NUMBER,
    Columns.DATE_OF_BIRTH,
    Columns.JOB,
    Columns.BANK_ACCOUNT,
    Columns.SSN,
]



class DataGenerator:
    """Generates tables of data in either row or column format.

    Can be used by itself, or within one of the classes to produce
    specific data formats.

    The return data is generated on the fly and returned as a named tuple of
    rows or columns.

    gen_rows()
    gen_table()
    """

    def __init__(
        self,
        table_format: TableFormat = TableFormat.ROW,
        columns: List[Columns] = DEFAULT_COLUMNS,
        seed: int = 0,
    ) -> None:

        self.table_format = table_format
        self.columns = columns
        self.headers = self._get_headers()
        self.data_generators = self._get_data_generators()
        self.faker = Faker(seed=seed)

    def _get_headers(self) -> List[str]:
        """ Retuns a list of headers for the columns """
        header_dict = {
            Columns.NAME: "Name",
            Columns.ADDRESS: "Address",
            Columns.PHONE_NUMBER: "Phone_Number",
            Columns.DATE_OF_BIRTH: "Date_of_Birth",
            Columns.JOB: "Job",
            Columns.BANK_ACCOUNT: "Bank_Account",
            Columns.SSN: "SSN"
        }

        return [header_dict[col] for col in self.columns]
    
    def _get_data_generators(self) -> List[Generator[Any, None, None]]:
        """ Returns a list of the custom data generators for the columns """

        generator_dict = {
            Columns.NAME: self._name_generator(),
            Columns.ADDRESS: self._address_generator(),
            Columns.PHONE_NUMBER: self._phone_number_generator(),
            Columns.DATE_OF_BIRTH: self._birth_date_generator(),
            Columns.JOB: self._job_generator(),
            Columns.BANK_ACCOUNT: self._bank_account_generator(),
            Columns.SSN: self._ssn_generator()
        }

        return [generator_dict[col] for col in self.columns]
       

    def _name_generator(self) -> str:
        """Infinite iterator to produce full names"""
        while True:
            prefix = f"{self.faker.prefix()} " if random.random() < 0.1 else ""
            name = self.faker.name()
            suffix = f" {self.faker.suffix()}" if random.random() < 0.1 else ""
            yield f"{prefix}{name}{suffix}"

    def _address_generator(self) -> Dict:
        """Infinite iterator of dictionaries of addresses
        {
            "address": str,
            "state": str,
            "city": str,
            "zipcode": int, # not actually smart, but good for testing types
        }
        """
        # fmt: off
        states_abbr = (
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        )
        # fmt: on
        while True:
            yield {
                "address": self.faker.street_address(),
                "state": random.choice(states_abbr),
                "city": self.faker.city(),
                "zipcode": self.faker.postcode(),
            }

    def _phone_number_generator(self) -> str:
        """Infinite iterator to phone numbers"""
        while True:
            yield self.faker.phone_number()

    def _birth_date_generator(self) -> str:
        """Infinite iterator to produce date of births"""
        while True:
            yield self.faker.date_of_birth(minimum_age=18, maximum_age=77)

    def _job_generator(self) -> str:
        """Infinite iterator to produce jobs"""
        while True:
            yield self.faker.job()

    def _bank_account_generator(self) -> str:
        """Infinite iterator to produce bank account IDs"""
        while True:
            yield self.faker.bban()

    def _ssn_generator(self) -> str:
        """Infinite iterator to produce social security numbers"""
        while True:
            yield self.faker.ssn()

    def gen_rows(self, num_rows: int = None) -> Iterator[namedtuple]:
        """ Returns an iterator of size `num_rows` of namedtuples in a row format """
        Row = namedtuple("Row", self.headers)
        return starmap(Row, islice(zip(*self.data_generators), num_rows))
        

    def gen_table(self, num_rows: int = None) -> namedtuple:
        """ Returns named a namedtuple of header & a list of data """
        Table = namedtuple("Table", self.headers)
        return Table(*(islice(data_generator, num_rows) for data_generator in self.data_generators))