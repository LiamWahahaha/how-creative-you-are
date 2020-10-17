# Kernel Catcher
**Kernel Catcher** is a project I built when I was a Data Engineering Fellow at Insight Data Science. It is a dashboard to allow admins of Kaggle competitions to catch plagiarized challenge submissions.


<hr/>
## How to install and get it up and running

### Run the unit test
> python3 -m unittest -v
<hr/>

## Motivation
Kaggle is the world's largest data science community. It contains a lot of data science competitions. It has been used not only for education but also for recruitment and competition with prizes. Therefore, fairness is highly important. Moreover, if you browsed their forum, you will find many users are complaining about plagiarism. How to improve the existing automated detection is one of the problems that the Kaggle staffs are working with.


## Tech stack & data pipeline
* **AWS S3**: All the kernel files and related competition metadata were hosted on S3.
* **Spark(PySpark)**: Apache Spark was used for 2 purposes:
  * Preprocessing: 
  * Similarity score calculation: Compute similarity score for different Kernels using pycode_similar
* **PostgreSQL**:

## Dataset
My data are collecting from two sources, one is from Kaggle using Kaggle API, another is from *Data from: Exploration and Explanation in Computational Notebooks*, which contains millions of Notebook files.

## Engineering challenges


## Trade-offs

## Links
* [Project Demo](http://www.similarity.work/)
* [Presentation Slides](https://docs.google.com/presentation/d/1Ro5ElbtOB5r7LXgql48T3CmUgvcPzyujvrsZED5XDiU/edit?usp=sharing)
