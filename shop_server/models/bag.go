package models

type Bag struct {
	ID       int    `json:"id"`
	User_ID  int    `json:"user_id"`
	Products string `json:"products"`
}

type User struct {
	ID      int    `json:"id"`
	API_key string `json:"api_key"`
}

type Product struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Price int    `json:"price"`
}