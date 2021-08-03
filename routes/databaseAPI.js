const express = require("express");
const router = express.Router();
const mysql = require('mysql');

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'fashiondb',
  insecureAuth: 'true',
})

// router.get("/", (req, res) => {
//     const sqlSelect = "SELECT * FROM fashiondb";
//     db.query(sqlSelect, (err, result) => {
//         res.send(result);
//     })
// })


router.post("/", (req, res) => {
    const sqlSelect = "SELECT * FROM fashiondb";
    db.query(sqlSelect, (err, result) => {
        res.send(result);
    })
})

router.post("/test", (req, res) => {
  res.send('HELLO')
})

module.exports = router;