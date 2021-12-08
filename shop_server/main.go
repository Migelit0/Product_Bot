package main

import (
	"fmt"
	"log"
	"os"

	"./models"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
)

func InitialMigration() *gorm.DB {
	e := godotenv.Load() //Загрузить файл .env
	if e != nil {
		fmt.Print(e)
	}

	username := os.Getenv("db_user")
	password := os.Getenv("db_pass")
	dbName := os.Getenv("db_name")
	dbHost := os.Getenv("db_host")

	dbUri := fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable password=%s", dbHost, username, dbName, password) //Создать строку подключения
	fmt.Println(dbUri)

	db, err := gorm.Open("postgres", dbUri)
	if err != nil {
		fmt.Print(err)
	}
	db.AutoMigrate(&models.User{}, &models.Bag{}, &models.Product{})
	defer db.Close()
	return db
}

func CheckError(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	e := godotenv.Load() //Загрузить файл .env
	if e != nil {
		fmt.Print(e)
	}

	username := os.Getenv("db_user")
	password := os.Getenv("db_pass")
	dbName := os.Getenv("db_name")
	dbHost := os.Getenv("db_host")

	dbUri := fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable password=%s", dbHost, username, dbName, password) //Создать строку подключения
	fmt.Println(dbUri)

	db, err := gorm.Open("postgres", dbUri)
	CheckError(err)

	defer db.Close()

	err = db.Ping() // проверяем работоспосбность базы
	CheckError(err)

	log.Println("Connected to db!")

	insertTestData := `insert into "Products"("Name", "Price", "Categories") values($1, $2, $3)`
	_, e = db.Exec(insertTestData, "Valio 3.5% 1l", 99.99, "молоко,напиток")
	CheckError(e)

}
