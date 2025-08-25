from enum import Enum
class CurrencyGroup(Enum):
    Foreign = 'F'
    All = 'A'

class Region(Enum):
    AllCountries = '3P'
    DevelopingAsiaAndPacific = '4Y'
    EmergingAndDevelopingEconomies = '4T'
    EuropeanDevelopedCountries = '5K'
    DevelopedCountries = '5R'
    DevelopingAfricaAndMiddleEast = '4R'
    DevelopingLatinAmericaAndCaribbean = '4U'
    DevelopingEurope = '3C'
    EuroArea = '5C'
    LiquidityAllCountries = '5J'
    LiquidityDevelopingEurope = '2A'

class Maturity(Enum):
    Total = 'A'
    LongTerm = 'K'
    ShortTerm = 'C'

class RateType(Enum):
    All = 'A'
    Fixed = 'C'

class IdsMeasure(Enum):
    Outstanding = 'I'
    Gross = 'C'
    Net = 'G'

class LbsMeasure(Enum):
    Stocks = 'S'
    Growth = 'G'
    BreakInStocks = 'B'
    FXAndBreakAdjusted = 'F'

class Position(Enum):
    Claims = 'C'
    Liabilities = 'L'

class Instrument(Enum):
    All = 'A'
    Credit = 'B'
    Debt = 'D'
    ShortTermDebt = 'M'
    Derivatives = 'I'
    LoansAndDeposits = 'G'
    Unallocated = 'U'

class Institution(Enum):
    All = 'A'
    DomesticBanks = 'D'
    ForeignBranches = 'B'
    ForeignSubsidiaries = 'S'

class PositionType(Enum):
    All = 'A'
    CrossBorder = 'N'
    CrossBorderAndLocal = 'I'
    Local = 'R'
    Unallocated = 'U'

class Sector(Enum):
    All = '1'
    Banks = 'B'
    Government = 'G'
    NonBanks = 'N'
    NonFinancialPrivateSector = 'S'
    NonFinancialSector = 'P'
    NonBankFinancialInstitution = 'F'

class CurrencyType(Enum):
    All = 'A'
    Domestic = 'D'
    Foreign = 'F'


class UnitOfMeasure(Enum):
    EUR = 'EUR'
    PercentageOfGDP = '770'
    USD = 'USD'
    PercentageOfGDPYoY = '771'
    JPY = 'JPY'