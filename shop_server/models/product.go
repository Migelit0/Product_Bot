package models

type Product struct {
	ID         int    `json:"id"`
	Name       string `json:"name"`
	Price      int    `json:"price"`
	Categories string `json:"categories"`
}
