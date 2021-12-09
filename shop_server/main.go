package main

import (
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func CheckError(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	err := godotenv.Load() //Загрузить файл .env
	CheckError(err)

	username := os.Getenv("db_user")
	password := os.Getenv("db_pass")
	dbName := os.Getenv("db_name")
	dbHost := os.Getenv("db_host")

	dbUri := fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable password=%s", dbHost, username, dbName, password) // Создать строку подключения
	fmt.Println(dbUri)

	conn, err := gorm.Open(postgres.Open(dbUri), &gorm.Config{}) // подключение к базе
	CheckError(err)

	db, err := conn.DB() // получаем управление базой
	CheckError(err)

	defer db.Close() // закрываем соединение

	err = db.Ping() // проверяем работоспосбность базы
	CheckError(err)

	log.Println("Connected to db!")

	insertTestData := `SELECT * FROM products`
	data, err := db.Exec(insertTestData) //, "Valio 3.5% 1l", 99.99, "молоко,напиток")
	CheckError(err)

	fmt.Println(data)

}
