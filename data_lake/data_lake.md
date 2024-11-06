# Data Lake Structure

This folder contains the **Data Lake** structure where all the scraped items will be stored before they undergo further processing and treatment.

## Why Use a NoSQL Database Like MongoDB?

I chose MongoDB, a NoSQL database, for the following reasons:

- **Flexibility in Storage**: MongoDB offers a flexible schema, which is ideal for storing the diverse and evolving data scraped from various e-commerce sites. 
- **Handling Inconsistent Data**: Different e-commerce platforms may present different data fields or even omit certain fields altogether. MongoDB allows us to store this data without worrying about enforcing a rigid schema, making it easier to accommodate these variations.
- **Scalability**: MongoDB can handle large volumes of data, which is essential as the amount of scraped information grows over time.
- **Ease of Future Changes**: As the scraping process evolves, MongoDB’s schema-less design allows us to add or remove fields as needed without significant restructuring. This adaptability makes it easier to accommodate new data points as we discover them.

The structure of the Data Lake enables easy storage, retrieval, and modification of raw scraped data before it is cleaned, transformed, and migrated into an SQL database for analysis.