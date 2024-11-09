// create a db
use e_commerce_db

// creating a collection for harpie data
db.createCollection("harpieCollection")

// delete all objects that does not have timestamp field
db.harpieCollection.deleteMany({"timestamp": {"$exists": false}})
