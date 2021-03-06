package main

import (
	"crypto/sha256"
	"crypto/subtle"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type application struct {
	auth struct {
		username string
		password string
	}
}

func (app *application) protectedHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "This is the protected handler")
}

func (app *application) basicAuth(next http.HandlerFunc) http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		username, password, ok := r.BasicAuth()
		if ok {
			usernameHash := sha256.Sum256([]byte(username))
			passwordHash := sha256.Sum256([]byte(password))
			expectedUsernameHash := sha256.Sum256([]byte(app.auth.username))
			expectedPasswordHash := sha256.Sum256([]byte(app.auth.password))

			usernameMatch := (subtle.ConstantTimeCompare(usernameHash[:], expectedUsernameHash[:]) == 1)
			passwordMatch := (subtle.ConstantTimeCompare(passwordHash[:], expectedPasswordHash[:]) == 1)

			if usernameMatch && passwordMatch {
				next.ServeHTTP(w, r)
				return
			}
		}

		w.Header().Set("WWW-Authenticate", `Basic realm="restricted", charset="UTF-8"`)
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
	})
}

func getDBConnection() (*gorm.DB, *sql.DB) {
	// подключаемся к базе
	dbUri := getConnectrionString()
	conn, err := gorm.Open(postgres.Open(dbUri), &gorm.Config{}) // подключение к базе
	CheckError(err)
	db, err := conn.DB() // получаем управление базой
	CheckError(err)
	err = db.Ping() // проверяем работоспосбность базы
	CheckError(err)
	log.Println("Connected to db!") // вот и подключились

	return conn, db
}

func addToBag(w http.ResponseWriter, r *http.Request) {
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	userId := vars["user_id"]
	productId := vars["product_id"]

	sqlRequest := `UPDATE users SET bag=(bag||';'||$1) WHERE id=$2;` // строка для импорта данных
	raw, err := db.Query(sqlRequest, productId, userId)
	CheckError(err)
	fmt.Println(raw)

	fmt.Fprintf(w, "true") // отправляем, что все круто
}

func getProduct(w http.ResponseWriter, r *http.Request) {
	conn, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	productId := vars["id"]

	sqlRequest := `SELECT * FROM "products" WHERE id = $1;`

	var product Product
	conn.Raw(sqlRequest, productId).Scan(&product)

	log.Println(product)
	err := json.NewEncoder(w).Encode(product)
	CheckError(err)
}

func showBag(w http.ResponseWriter, r *http.Request) {
	conn, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	userId := vars["user_id"]

	sqlRequest := `SELECT bag FROM "users" WHERE id=$1 LIMIT 1;` // получаем корзину данного пользователя

	var userBagStr string
	conn.Raw(sqlRequest, userId).Scan(&userBagStr)

	userBag := strings.Split(userBagStr, ";")

	var products []Product

	for _, productId := range userBag {
		if productId != "" {	// потому что первый фантомный
			sqlRequest := `SELECT * FROM "products" WHERE id=$1;` // инвалидное решение на скорую руку

			var product Product
			conn.Raw(sqlRequest, productId).Scan(&product)
			products = append(products, product)
		}
	}

	log.Println(products)
	err := json.NewEncoder(w).Encode(products)
	CheckError(err)
}

func clearBag(w http.ResponseWriter, r *http.Request) {
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	fmt.Println(vars)
	userId := vars["user_id"]

	fmt.Println("UserID:")
	fmt.Println(userId)

	sqlRequest := `UPDATE users SET bag=';' WHERE id=$1;` // строка для очистки данных
	raw, err := db.Query(sqlRequest, userId)

	CheckError(err)
	fmt.Println(raw)

	fmt.Fprintf(w, "true") // отправляем, что все круто
}

func searchProductByCategory(w http.ResponseWriter, r *http.Request) {
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	productCategory := vars["category"]

	sqlRequest := `SELECT * FROM "products" WHERE categories LIKE $1;` // строка для импорта данных

	raw, err := db.Query(sqlRequest, "%"+productCategory+"%")
	CheckError(err)

	var products []Product
	for raw.Next() { // добавляем все данные из бд в массив
		p := Product{}
		err := raw.Scan(&p.ID, &p.Name, &p.Price, &p.Categories)
		CheckError(err)
		products = append(products, p)
	}

	log.Println(products)
	err = json.NewEncoder(w).Encode(products)
	CheckError(err)
}

func searchProductByName(w http.ResponseWriter, r *http.Request) {
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	vars := mux.Vars(r)
	productName := vars["name"]
	maxValue := 0.3

	sqlRequest := `SELECT * FROM "products" WHERE similarity(name, $1) >= $2;` // строка для импорта данных

	raw, err := db.Query(sqlRequest, productName, maxValue)
	CheckError(err)

	var products []Product
	for raw.Next() { // добавляем все данные из бд в массив
		p := Product{}
		err := raw.Scan(&p.ID, &p.Name, &p.Price, &p.Categories)
		CheckError(err)
		products = append(products, p)
	}

	log.Println(products)
	err = json.NewEncoder(w).Encode(products)
	CheckError(err)
}

func createUser(w http.ResponseWriter, r *http.Request) {
	var isOk int
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	sqlRequest := `INSERT INTO users (bag) VALUES(' ') RETURNING id;` // строка для импорта данных
	raw, err := db.Query(sqlRequest)
	CheckError(err)

	for raw.Next() {
		err = raw.Scan(&isOk)
		CheckError(err)
	}

	fmt.Println(isOk)

	err = json.NewEncoder(w).Encode(isOk)
	CheckError(err)
}

func getMaxId(w http.ResponseWriter, r *http.Request) {
	var productId int
	_, db := getDBConnection()
	defer db.Close() // закрываем соединение

	sqlRequest := `SELECT id FROM products ORDER BY (-1 * id) LIMIT 1;` // получение максимального айди (впадлу думать я устал)
	raw, err := db.Query(sqlRequest)
	CheckError(err)
	fmt.Println(raw)

	for raw.Next() {
		err = raw.Scan(&productId)
		CheckError(err)
	}

	err = json.NewEncoder(w).Encode(productId)
	CheckError(err)
}

func homePage(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to the HomePage!")
	fmt.Println("Endpoint Hit: homePage")
}

func getConnectrionString() string {
	err := godotenv.Load("/home/server/telega/product_bot/shop_server/.env") //Загрузить файл .env
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
	app := new(application)
	//fmt.Println(os.Getenv("auth_username"))

	err := godotenv.Load("/home/server/telega/product_bot/shop_server/.env") //Загрузить файл .env

	fmt.Println(err)
	CheckError(err)
	app.auth.username = os.Getenv("AUTH_USERNAME")
	app.auth.password = os.Getenv("AUTH_PASSWORD")
	port := os.Getenv("http_port")

	if app.auth.username == "" {
		log.Fatal("basic auth username must be provided")
	}

	if app.auth.password == "" {
		log.Fatal("basic auth password must be provided")
	}

	myRouter := mux.NewRouter()
	myRouter.HandleFunc("/", app.basicAuth(homePage))
	myRouter.HandleFunc("/bag/add/{user_id}/{product_id}", app.basicAuth(addToBag))
	myRouter.HandleFunc("/bag/clear/{user_id}", app.basicAuth(clearBag))
	myRouter.HandleFunc("/bag/show/{user_id}", app.basicAuth(showBag))
	myRouter.HandleFunc("/product/{id}", app.basicAuth(getProduct))
	myRouter.HandleFunc("/search/product/category/{category}", app.basicAuth(searchProductByCategory))
	myRouter.HandleFunc("/search/product/name/{name}", app.basicAuth(searchProductByName))
	myRouter.HandleFunc("/new/user/demo", app.basicAuth(createUser))
	myRouter.HandleFunc("/product/max/demo", app.basicAuth(getMaxId))

	srv := &http.Server{
		Addr:         port,
		Handler:      myRouter,
		IdleTimeout:  time.Minute,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	log.Printf("starting shop api on %s", srv.Addr)
	err = srv.ListenAndServe()
	log.Fatal(err)

}

func CheckError(err error) {
	if err != nil {
		panic(err)
	}
}

type Bag struct {
	ID       int    `json:"id"`
	User_ID  int    `json:"user_id"`
	Products string `json:"products"`
}

type Product struct {
	ID         int     `json:"id"`
	Name       string  `json:"name"`
	Price      float64 `json:"price"`
	Categories string  `json:"categories"`
}
type User struct {
	ID      int    `json:"id"`
	API_key string `json:"api_key"`
}
