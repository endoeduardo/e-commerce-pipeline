// create a db
use("e_commerce_db")

// creating a collection for harpie data
db.createCollection("ECommerceCollection",
	{
		validator:{
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "product_name", "product_link", "one_time_payment",
                    "quantity_of_payments", "payments_value", "color",
                    "variation", "timestamp"
                ],
                "properties": {
                    "product_name": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "product_link": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "one_time_payment": {
                        "bsonType": "double",
                        "description": "must be a floating-point number and is required"
                    },
                    "quantity_of_payments": {
                        "bsonType": "int",
                        "description": "must be an integer and is required"
                    },
                    "payments_value": {
                        "bsonType": "double",
                        "description": "must be a floating-point number and is required"
                    },
                    "variation": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["size", "in_stock"],
                            "properties": {
                                "size": {
                                    "bsonType": "string",
                                    "description": "must be a string and is required"
                                },
                                "in_stock": {
                                    "bsonType": "bool",
                                    "description": "must be a boolean and is required"
                                }
                            }
                        },
                        "description": "must be an array of objects and is required"
                    },
                    "timestamp": {
                        "bsonType": "string",
                        "description": "must be a string in date format and is required"
                    }
                }
            }},
        validationAction: "warn"
	})

// modifying an existing collection
db.runCommand( { collMod: "ECommerceCollection",
    validator:{
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "product_name", "product_link", "one_time_payment",
                "quantity_of_payments", "payments_value", "color",
                "variation", "timestamp"
            ],
            "properties": {
                "product_name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "product_link": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "one_time_payment": {
                    "bsonType": "double",
                    "description": "must be a floating-point number and is required"
                },
                "quantity_of_payments": {
                    "bsonType": "int",
                    "description": "must be an integer and is required"
                },
                "payments_value": {
                    "bsonType": "double",
                    "description": "must be a floating-point number and is required"
                },
                "variation": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["size", "in_stock"],
                        "properties": {
                            "size": {
                                "bsonType": "string",
                                "description": "must be a string and is required"
                            },
                            "in_stock": {
                                "bsonType": "bool",
                                "description": "must be a boolean and is required"
                            }
                        }
                    },
                    "description": "must be an array of objects and is required"
                },
                "timestamp": {
                    "bsonType": "string",
                    "description": "must be a string in date format and is required"
                }
            }
        }},
    validationAction: "warn"
})


// delete all objects that does not have timestamp field
db.ECommerceCollection.deleteMany({"timestamp": {"$exists": false}})

// fiding the invalid or valid documets only
let ECommerceCollection = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "product_name", "product_link", "one_time_payment",
            "quantity_of_payments", "payments_value", "color",
            "variation", "timestamp"
        ],
        "properties": {
            "product_name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "product_link": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "one_time_payment": {
                "bsonType": "double",
                "description": "must be a floating-point number and is required"
            },
            "quantity_of_payments": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "payments_value": {
                "bsonType": "double",
                "description": "must be a floating-point number and is required"
            },
            "variation": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["size", "in_stock"],
                    "properties": {
                        "size": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "in_stock": {
                            "bsonType": "bool",
                            "description": "must be a boolean and is required"
                        }
                    }
                },
                "description": "must be an array of objects and is required"
            },
            "timestamp": {
                "bsonType": "string",
                "description": "must be a string in date format and is required"
            }
        }
    }
}
db.ECommerceCollection.find({$nor: [ECommerceCollection]})