# write your code here
import csv

from os import path
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import func, desc


Base = declarative_base()

class Companies(Base):
    __tablename__ = 'companies'

    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)


class Financial(Base):
    __tablename__ = 'financial'

    ticker = Column(String, primary_key=True)
    ebitda = Column(Float)
    sales = Column(Float)
    net_profit = Column(Float)
    market_price = Column(Float)
    net_debt = Column(Float)
    assets = Column(Float)
    equity = Column(Float)
    cash_equivalents = Column(Float)
    liabilities = Column(Float)


# noinspection SpellCheckingInspection
class InvestorCalculator:
    def __init__(self):
        # Connect to database if it exists
        if path.exists("investor.db"):
            self.engine = create_engine('sqlite:///investor.db')
            session = sessionmaker(bind=self.engine)
            self.session = session()
        # Otherwise, create database and tables
        else:
            self.engine = create_engine('sqlite:///investor.db')
            Base.metadata.create_all(self.engine)
            session = sessionmaker(bind=self.engine)
            self.session = session()

            # Open input csvs
            companies_file_handler = open('companies.csv', 'r')
            companies = csv.DictReader(companies_file_handler)
            financial_file_handler = open('financial.csv', 'r')
            financial = csv.DictReader(financial_file_handler)

            # Process input csvs
            for company in companies:
                clean_company = {key: None if value == '' else value for (key, value) in company.items()}
                company_mapped = Companies(ticker=clean_company['ticker'],
                                           name=clean_company['name'],
                                           sector=clean_company['sector'])
                self.session.add(company_mapped)
            self.session.commit()
            for fin in financial:
                clean_fin = {key: None if value == '' else value for (key, value) in fin.items()}
                fin_mapped = Financial(ticker=clean_fin['ticker'],
                                       ebitda=clean_fin['ebitda'],
                                       sales=clean_fin['sales'],
                                       net_profit=clean_fin['net_profit'],
                                       market_price=clean_fin['market_price'],
                                       net_debt=clean_fin['net_debt'],
                                       assets=clean_fin['assets'],
                                       equity=clean_fin['equity'],
                                       cash_equivalents=clean_fin['cash_equivalents'],
                                       liabilities=clean_fin['liabilities'])
                self.session.add(fin_mapped)
            self.session.commit()

            # Close out files
            companies_file_handler.close()
            financial_file_handler.close()

        print('Welcome to the Investor Program!')

        while True:
            print('MAIN MENU')
            print('0 Exit')
            print('1 CRUD operations')
            print('2 Show top ten companies by criteria')
            print()
            choice = input('Enter an option: ')
            if choice == '0':
                self.session.close_all()
                print('Have a nice day!')
                return
            elif choice == '1':
                self.crud_menu()
            elif choice == '2':
                self.top_ten_menus()
            else:
                print('Invalid option!')

    def crud_menu(self):
        print('CRUD MENU')
        print('0 Back')
        print('1 Create a company')
        print('2 Read a company')
        print('3 Update a company')
        print('4 Delete a company')
        print('5 List all companies')
        print()
        choice = input('Enter an option: ')
        if choice == '0':
            pass
        elif choice == '1':
            self.create_company()
        elif choice == '2':
            self.read_company()
        elif choice == '3':
            self.update_company()
        elif choice == '4':
            self.delete_company()
        elif choice == '5':
            self.list_companies()
        else:
            print('Invalid option!')
        print()
        return

    def create_company(self):
        ticker = input("Enter ticker (in the format 'MOON')")
        company = input("Enter company (in the format 'Moon Corp'):")
        industry = input("Enter industries (in the format 'Technology'):")
        ebitda = float(input("Enter ebitda (in the format '987654321'):"))
        sales = float(input("Enter sales price (in the format '987654321'):"))
        net_profit = float(input("Enter net profit (in the format '987654321'):"))
        market_price = float(input("Enter market price (in the format '987654321'):"))
        net_debt = float(input("Enter net debt (in the format '987654321'):"))
        assets = float(input("Enter assets (in the format '987654321'):"))
        equity = float(input("Enter equity (in the format '987654321'):"))
        cash_equivalents = float(input("Enter cash equivalents (in the format '987654321'):"))
        liabilities = float(input("Enter liabilities (in the format '987654321'):"))

        # Insert company-related data
        company_data = Companies(ticker=ticker,
                                 name=company,
                                 sector=industry)
        self.session.add(company_data)

        # Insert financial-related data
        financial_data = Financial(ticker=ticker,
                                   ebitda=ebitda,
                                   sales=sales,
                                   net_profit=net_profit,
                                   market_price=market_price,
                                   net_debt=net_debt,
                                   assets=assets,
                                   equity=equity,
                                   cash_equivalents=cash_equivalents,
                                   liabilities=liabilities)
        self.session.add(financial_data)

        # Commit
        self.session.commit()
        print('Company created successfully!')

    def search_company(self) -> tuple:
        company_query_text = input("Enter company name: ")
        results = self.session.query(Companies).filter(Companies.name.like(f"%{company_query_text}%")).all()
        if len(results) == 0:
            print('Company not found!')
            return None, None
        for i in range(len(results)):
            print(f"{i} {results[i].name}")
        selection = int(input("Enter company number: "))
        if selection < 0 or selection >= len(results):
            print('Company not found!')
            return None, None
        return str(results[selection].ticker), str(results[selection].name)

    def read_company(self):
        company_ticker, company_name = self.search_company()
        if company_ticker:
            financial_data = func.round(self.session.query(Financial).filter(Financial.ticker == company_ticker).first(), 2)
            print(f"{company_ticker} {company_name}")
            print(f"P/E = {financial_data.market_price / financial_data.net_profit if financial_data.market_price and financial_data.net_profit else None}")
            print(f"P/S = {financial_data.market_price / financial_data.sales if financial_data.market_price and financial_data.sales else None}")
            print(f"P/B = {financial_data.market_price / financial_data.assets if financial_data.market_price and financial_data.assets else None}")
            print(f"ND/EBITDA = {financial_data.net_debt / financial_data.ebitda if financial_data.net_debt and financial_data.ebitda else None}")
            print(f"ROE = {financial_data.net_profit / financial_data.equity if financial_data.net_profit and financial_data.equity else None}")
            print(f"ROA = {financial_data.net_profit / financial_data.assets if financial_data.net_profit and financial_data.assets else None}")
            print(f"L/A = {financial_data.liabilities / financial_data.assets if financial_data.liabilities and financial_data.assets else None}")

    def update_company(self):
        company_ticker, company_name = self.search_company()
        if company_ticker:
            financial_update = {"ebitda": float(input("Enter ebitda (in the format '987654321'):")),
                                "sales": float(input("Enter sales price (in the format '987654321'):")),
                                "net_profit": float(input("Enter net profit (in the format '987654321'):")),
                                "market_price": float(input("Enter market price (in the format '987654321'):")),
                                "net_debt": float(input("Enter net debt (in the format '987654321'):")),
                                "assets": float(input("Enter assets (in the format '987654321'):")),
                                "equity": float(input("Enter equity (in the format '987654321'):")),
                                "cash_equivalents": float(input("Enter cash equivalents (in the format '987654321'):")),
                                "liabilities": float(input("Enter liabilities (in the format '987654321'):"))}

            self.session.query(Financial).filter(Financial.ticker == company_ticker).update(financial_update)
            self.session.commit()
            print('Company updated successfully!')

    def delete_company(self):
        company_ticker, company_name = self.search_company()
        if company_ticker:
            self.session.query(Companies).filter(Companies.ticker == company_ticker).delete()
            self.session.query(Financial).filter(Financial.ticker == company_ticker).delete()
            self.session.commit()
            print('Company deleted successfully!')

    def list_companies(self):
        print('COMPANY LIST')
        all_companies = self.session.query(Companies).order_by(Companies.ticker.asc()).all()
        for company in all_companies:
            print(f"{company.ticker} {company.name} {company.sector}")

    def top_ten_menus(self):
        print('TOP TEN MENU')
        print('0 Back')
        print('1 List by ND/EBITDA')
        print('2 List by ROE')
        print('3 List by ROA')
        print()
        choice = input('Enter an option: ')
        if choice == '0':
            pass
        elif choice == '1':
            self.top_ten_nd_ebitda()
        elif choice == '2':
            self.top_ten_roe()
        elif choice == '3':
            self.top_ten_roa()
        else:
            print('Invalid option!')
        print()
        return

    def top_ten_nd_ebitda(self):
        print('TICKER ND/EBITDA')
        top_nd_ebitda = (self.session.query(Financial.ticker,
                                           func.round((Financial.net_debt / Financial.ebitda), 2).label('nd_ebitda'))
                         .order_by(desc('nd_ebitda')).limit(10).all())
        for nd_ebitda in top_nd_ebitda:
            print(f"{nd_ebitda.ticker} {nd_ebitda.nd_ebitda}")

    def top_ten_roe(self):
        print('TICKER ROE')
        top_roe = (self.session.query(Financial.ticker,
                                     func.round((Financial.net_profit / Financial.equity), 2).label('roe'))
                   .order_by(desc('roe')).limit(10).all())
        for roe in top_roe:
            print(f"{roe.ticker} {roe.roe}")

    def top_ten_roa(self):
        print('TICKER ROA')
        top_roa = (self.session.query(Financial.ticker,
                                     func.round((Financial.net_profit / Financial.assets), 2).label('roa'))
                   .order_by(desc('roa')).limit(10).all())
        for roa in top_roa:
            print(f"{roa.ticker} {roa.roa}")


if __name__ == '__main__':
    InvestorCalculator()
