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

router.get("/", (req, res) => {
    const sqlSelect = "SELECT * FROM fashiondb";
    db.query(sqlSelect, (err, result) => {
        res.send(result);
    })
})

router.post ("/update", function(req, res, next) {
  const name = req.body.data.name;
  const weblink = req.body.data.weblink;
  const imagelink = req.body.data.imglink;
  const bodyshape = req.body.data.bodyshape;
  const types = req.body.data.types;
  const price = req.body.data.price;
  const style = req.body.data.style;

  const sqlInsert = "INSERT INTO fashiondb (name, weblink, imglink, bodyshape, types, price, style) VALUES (?, ?, ?, ?, ?, ?, ?)";
  db.query(sqlInsert, [name, weblink, imagelink, bodyshape, types, price, style], (err, result) => {
    console.log(result);
  })
});

module.exports = router;