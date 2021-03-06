import numpy as np
import os
import requests
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import pandas.io.sql as pdsql
from config import pg_user, pg_password, db_name
from flask import Flask, jsonify, render_template, abort, redirect

#################################################
# Database Setup
##################################################

connection_string = f"{pg_user}:{pg_password}@localhost:5432/{db_name}"
engine = create_engine(f'postgresql://{connection_string}')

# checking the table names
engine.table_names()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/comparison")
def comparison():
    return render_template("comparison.html")


@app.route('/searchbyyear')
def searchbyyear():
    sqlStatement = """
    SELECT year, SUM ("Cancer" + "cardiovascular" + "stroke" + "depression" + "rehab" + "vaccine" + "diarrhea" + "obesity" + "diabetes") AS Searches  
    FROM search_condition 
    GROUP BY year
    ORDER BY year;
    """
    df = pdsql.read_sql(sqlStatement, engine)
    df.set_index('year', inplace=True)
    df = df.to_json(orient='table')
    result = json.loads(df)
    return jsonify(result)


@app.route('/searchyearandcondition')
def searchyearandcondition():
    sqlStatement = """
    SELECT year, SUM ("Cancer") AS Cancer,SUM ("cardiovascular") As Cardiovascular,SUM ("stroke") As Stroke,SUM ("depression") As Depression,SUM ("rehab") AS Rehab,SUM ("vaccine") AS Vaccine, SUM ("diarrhea") AS Diarrhea, SUM("obesity") AS Obesity, SUM ("diabetes") AS Diabetes    
    FROM search_condition 
    GROUP BY year

    """
    df = pdsql.read_sql(sqlStatement, engine)
    df.set_index('food_code', inplace=True)
    df = df.to_json(orient='table')

    return df


@app.route('/descriptioncategory')
def descriptioncategory():
    sqlStatment = """
    SELECT d.category_num, n.main_food_description,c.category, d.wweia_category_code, p.wweia_category_description, p.portion_description, p.portion_weight_g, n.energy_kcal, n.protein_g, n.sugars_total_g, n.carbohydrate_g, n.total_fat_g
    FROM searchbyyear AS n
    INNER JOIN portionsandweights AS p
    ON n.food_code = p.food_code
    INNER JOIN descriptioncategory AS d
    ON n.wweia_category_code = d.wweia_category_code
    INNER JOIN category AS c
    ON d.category_num = c.category_num
    """

    df = pdsql.read_sql(sqlStatment, engine)
    df.set_index('category', inplace=True)
    df = df.to_json(orient='table')

    return df


@app.route('/category')
def category():

    df = pdsql.read_sql("SELECT * FROM category", engine)
    df.set_index('category_num', inplace=True)
    df = df.to_json(orient='table')

    return df


@app.route('/dailyvalue')
def dailyvalue():

    df = pdsql.read_sql("SELECT * FROM dailyvalue", engine)
    df.set_index('dv_id', inplace=True)
    df = df.to_json(orient='table')

    return df


if __name__ == '__main__':
    app.run(debug=True)
