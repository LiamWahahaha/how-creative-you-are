# Kernel Catcher
 
<hr/>

**Kernel Catcher** is a project I built when I was a Data Engineering Fellow at Insight Data Science. It is a dashboard to allow admins of Kaggle competitions to catch plagiarized challenge submissions.

## Table of contents

<hr/>

* [Motivation](README.md#motivation)
* [Architecture](README.md#architecture)
* [Dataset](README.md#dataset)
* [Engineering challenges](README.md#engineering-challenges)
* [Setup](README.md#setup)
* [Links](README.md#links)

## Motivation

<hr/>

Kaggle is the world's largest data science community. It contains a lot of data science competitions. It has been used not only for education but also for recruitment and competition with prizes. Therefore, fairness is highly important. Moreover, if you browsed their forum, you will find many users are complaining about plagiarism. How to improve the existing automated detection is one of the problems that the Kaggle staffs are working with.

## Architecture

<hr/>

* **AWS S3**: All the kernel files and related competition metadata were hosted on S3.
* **Spark(PySpark)**: Apache Spark was used for 2 purposes:
  * Preprocessing: 
  * Similarity score calculation: Compute similarity score for different Kernels using pycode_similar
* **PostgreSQL**:

## Dataset

<hr/>

My data are collecting from two sources, one is from Kaggle using Kaggle API, another is from *[Data from: Exploration and Explanation in Computational Notebooks](https://library.ucsd.edu/dc/collection/bb6931851t)*, which contains millions of Notebook files.

## Engineering challenges

<hr/>

To have a similarity matrix, we have to do a pairwise comparison between kernels. When each kernel is comparing with every other, we have a quadratic time complexity. For any competition that reaches 90 thousand submissions, it will require billions of comparisons. If calculating a single comparison requires 1 ms, then it will need at least one month to process that competition when we calculate with only one CPU. 

To reduce the processing time, I use three approach as follows:
* Skip unnecessary comparisons by:
  * Only compare different user's submissions. This is reasonable because even one's submission is highly similar to his or her previous submission, we still won't treat this situation as plagiarism.
  * Skip comparisons if the imported packages of kernels are different. This assumption requires further validation. The concept is that if they used different packages or even different functions, then they are solving the problem with different approaches.
* Reduce the calculation time:
  * When it is necessary to calculate the similarity score, I only feed in code cells instead of whole notebook data. Therefore, the pycode_similar will only compare two KB files instead of two MB files. 
* With the power of distribution and parallel computing:
  * Can further reduce at least 75% of the time if we use four instances


## Setup

<hr/>

This project was built using an Apache Spark 2.4.7 / Hadoop 2.7 binary downloaded from spark.apache.org. A driver from jdbc.postgresql.org should added in spark/jars/ and configurations should be added to spark-defaults.conf, since it writes data to PostgreSQL. The dashboard application was built with Vue and Flask. 

* **Data Ingestion**:
  * Download kernel from Kaggle using Kaggle API
  ```
  cd ingestion
  python3 -m venv venv
  . venv/bin/activate
  pip3 install -r requirements.txt
  ```
  * How to get a competition id? Use the commandline tool and search with competition keywords:
  ```
  python3 data_collection.py --search [competition keywords]
  ```
  * How to get a competition metadata and all the related kernels?
  ```
  python3 data_collection.py --save [competition_id]
  ```
  * After having the corresponding csv file and kernels, store it to specified S3 bucket
* **Data processing**:
  * Install virtual environment and install packages
  ```
  python3 -m venv venv
  . venv/bin/activate
  cd processing
  ```
  * Preprocess:
  ```
  spark-submit preprocessing.py
  ```
  * Calculate similarity score:
  ```
  spark-submit similarity_calculation.py
  ```

### Run the unit test
```
cd processing
python3 -m unittest -v
```

## Links

<hr/>

* [Project Demo](http://www.similarity.work/)
* [Presentation Slides](https://docs.google.com/presentation/d/1Ro5ElbtOB5r7LXgql48T3CmUgvcPzyujvrsZED5XDiU/edit?usp=sharing)
