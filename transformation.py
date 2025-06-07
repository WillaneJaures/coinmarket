from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, regexp_replace,split,trim, element_at, when, array_contains,try_element_at,size,expr,lower,count,mean,desc,asc,avg,round



spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.jars", "/home/sabou/Documents/extracted/usr/share/java/mysql-connector-java-9.3.0.jar") \
    .getOrCreate()


#read the csv file
df = spark.read.csv("/home/sabou/Documents/project1/coinmarket.csv", header=True, inferSchema=True)

#display the schema
df.show(5)

#remove CFA from column price and convert to float
df1 = df.withColumn(
    "price",
    expr("try_cast(regexp_replace(regexp_replace(price, 'CFA', ''), ' ', '') as bigint)")
)

#remove minutes from column time, convert it to int and rename it
df2 = df1.withColumnRenamed("Time", "Posted_at") 
#df2.show(5)

df_clean = df2.withColumn("Posted_at", trim(lower(col("Posted_at"))))
df_t = df_clean.filter(~col("Posted_at").rlike("sénégal|dakar"))


#split column location into separated column (area, city)
split_col = split(col("Location"), ",")
df3 = df_t.withColumn("Area", when(size(split_col) > 0, trim(element_at(split_col,1)))) \
          .withColumn("City", when(size(split_col) > 1, trim(element_at(split_col, 2)))) \
         #.withColumn("City", when(size(split_col) > 2, trim(element_at(split_col, 3))))
      
#df3.show(5)
df4 = df3.drop("Location","Etat")
#df4.show(5)


df5 = df4.withColumn("City", when(col("City") == "Sénégal", col("Area")).otherwise(col("City")))
##tr1 = tr0.groupBy("City", "Area").count()
##tr1.show()

#deal with duplicated values
df6  = df5.dropDuplicates()

#deal with missing values

avg_price = df6.select(mean(col("price"))).first()[0]
df_filed = df6.fillna({"price":avg_price})

df_final = df_filed.fillna({"Livraison": "indisponible"})

df_final.show(10)
##cc = df_filed1.filter((col("City").isNull())).count()
##print(f"valeur manquante City: {cc}")
#cc = df4.select("Area").distinct()
#cc.show(20)



df_final.write \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306/coinmarket") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "Product") \
    .option("user", "root") \
    .option("password", "mysql") \
    .mode("overwrite") \
    .save()

#top 10 produits les plus vendus
top_name = df_final.groupBy("Name").count().orderBy(desc("count"))
#top_name.show(10)

# top 10 des produits les plus vendus

top_product = df_final.groupBy("Product").count().orderBy(desc("count"))
#top_product.show(10)


#zone la plus actif
top_area = df_final.groupBy("Area").count().orderBy(desc("count"))
#top_area.show()


#prix moyen d'une voiture
avg_price_voiture = df_final.filter(col("Product") == "Voitures").select(round(avg("price"),4).alias("avg_price"))
avg_price_voiture.show()

df_final.filter(col("Product") == "Voitures").select("Name","price").orderBy(desc("price")).show(20) 

#send to mysql


