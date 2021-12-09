package main

import (
	"Product_Bot/shop_server/models"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func addToBag(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userId := vars["id"]

	fmt.Println(w, "ID: "+userId)
}

func getProduct(w http.ResponseWriter, r *http.Request) {
	// подключаемся к базе
	dbUri := getConnectrionString()
	conn, err := gorm.Open(postgres.Open(dbUri), &gorm.Config{}) // подключение к базе
	CheckError(err)

	db, err := conn.DB() // получаем управление базой
	CheckError(err)
	defer db.Close() // закрываем соединение
	err = db.Ping()  // проверяем работоспосбность базы
	CheckError(err)

	log.Println("Connected to db!") // вот и подключились

	vars := mux.Vars(r)
	productId := vars["id"]

	sqlRequest := `SELECT * FROM "products" WHERE id = $1;`

	var product models.Product
	conn.Raw(sqlRequest, productId).Scan(&product)

	log.Println(product)
	err = json.NewEncoder(w).Encode(product)
	CheckError(err)
}

func searchProductByCategory(w http.ResponseWriter, r *http.Request) {
	// подключаемся к базе
	dbUri := getConnectrionString()
	conn, err := gorm.Open(postgres.Open(dbUri), &gorm.Config{}) // подключение к базе
	CheckError(err)
	db, err := conn.DB() // получаем управление базой
	CheckError(err)
	defer db.Close() // закрываем соединение
	err = db.Ping()  // проверяем работоспосбность базы
	CheckError(err)
	log.Println("Connected to db!") // вот и подключились

	vars := mux.Vars(r)
	productCategory := vars["category"]

	sqlRequest := `SELECT * FROM "products" WHERE categories LIKE $1;`

	var product models.Product
	conn.Raw(sqlRequest, "%"+productCategory+"%").Scan(&product)

	log.Println(product)
	err = json.NewEncoder(w).Encode(product)
	CheckError(err)
}

func homePage(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to the HomePage!")
	fmt.Println("Endpoint Hit: homePage")
}

func handleRequests() {
	myRouter := mux.NewRouter().StrictSlash(true) // создаем обработчик запросов
	myRouter.HandleFunc("/", homePage)
	myRouter.HandleFunc("/bag/{id}", addToBag)
	myRouter.HandleFunc("/product/{id}", getProduct)
	myRouter.HandleFunc("/search/product/{category}", searchProductByCategory)
	log.Fatal(http.ListenAndServe(":5445", myRouter)) // запускаем обработчик ранее объявленного
}

func getConnectrionString() string {
	err := godotenv.Load("C:\\Users\\mmpan\\go\\src\\Product_Bot\\shop_server\\.env") //Загрузить файл .env
	fmt.Println(err)
	CheckError(err)

	username := os.Getenv("db_user")
	password := os.Getenv("db_pass")
	dbName := os.Getenv("db_name")
	dbHost := os.Getenv("db_host")

	dbUri := fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable password=%s", dbHost, username, dbName, password) // Создать строку подключения
	return dbUri
}

func main() {
	fmt.Println("Started REST API v0.1 - Shop Server")
	handleRequests()

}

func CheckError(err error) {
	if err != nil {
		panic(err)
	}
}
