'''
Descripttion: 
version: 
Author: Author
Date: 2023-07-03 10:10:00
LastEditors: Author
LastEditTime: 2023-07-26 13:00:39
'''
import boto3
import pandas as pd
from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP, Float
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from entities.alarm import Alarm

from soa_kafka_python.utils import get_db_secrets

class DataAccessManager():
    def __init__(self, hyper_params, db_config) -> None:
        if(hyper_params["db_mode"] == "aws_db"):
            secrets = get_db_secrets(db_config["aws_db"]["db_secret_name"])
            connection_url = URL.create(
                    db_config["aws_db"]["db_type"],
                    username=secrets['username'],
                    password=secrets['password'],
                    host=db_config["aws_db"]["host"],
                    port=db_config["aws_db"]["db_port"],
                    database=db_config["aws_db"]["db_name"],
                    # query={
                    #     "driver": driver,
                    #     "authentication": authentication,
                    # },
                )
        elif(hyper_params["db_mode"] == "local_db"):
            connection_url = URL.create(
                    db_config["local_db"]["db_type"],
                    username=db_config["local_db"]['username'],
                    password=db_config["local_db"]['password'],
                    host=db_config["local_db"]["host"],
                    port=db_config["local_db"]["db_port"],
                    database=db_config["local_db"]["db_name"],
            )
        elif(hyper_params["db_mode"] == "tmp_db"):
            connection_url = f"sqlite:///{db_config['tmp_db']['db_name']}?check_same_thread=False"
        
        #print(connection_url)
        self.__session = None
        self.__engine = create_engine(connection_url,
                         echo=False,
                         pool_size=1,
                         max_overflow=0,
                         pool_recycle=3600,
                         pool_pre_ping=True,
                         pool_use_lifo=True)
        #self.__engine = create_engine(connection_url)

    def __create_db_session(self, engine):
        self.__session = sessionmaker(bind=engine)()
        # todo: setup connection pooling properties
        return self.__session

    def close(self) -> None:
        if self.__session:
            self.__session.close_all()
        self.__engine = None

    def add_rows(self, rows) -> None:
        session = self.__create_db_session(self.__engine)
        print(rows)
        session.add_all(rows)
        session.commit()
        
    def update_rows(self, rows, table_name) -> None:
        to_save_data = []
        session = self.__create_db_session(self.__engine)
        for row in rows:
            session.query(table_name).filter(table_name.Id == row[0]).update(row)
        session.commit()
        
    def delete_rows(self, conditions, table_name) -> None:
        session = self.__create_db_session(self.__engine)
        q = session.query(table_name).filter(*conditions)
        #print(q.statement.compile(compile_kwargs={'literal_binds': True}))
        rows = q.all()
        
        for row in rows:
            session.delete(row)
        session.commit()
        
    def query_rows(self, conditions, table_name) -> list:
        session = self.__create_db_session(self.__engine)
        query = session.query(table_name).filter(*conditions)
        
        return pd.read_sql(query.statement, self.__engine)