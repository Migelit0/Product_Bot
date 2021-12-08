package models

type Bag struct {
	ID       int    `json:"id"`
	User_ID  int    `json:"user_id"`
	Products string `json:"products"`
}
