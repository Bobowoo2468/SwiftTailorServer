const express = require("express");
const router = express.Router();
const mysql = require('mysql');
const cors = require('cors');

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

// router.post("/test", (req, res) => {
//   res.send('HELLO');
//   console.log('HELLO');
// })

// router.post("/test", (req, res) => {
//   const obj = {"adult": "Hello, World", "baby" : "Sam"};
//   res.send(obj);
//   console.log(obj);
// })

router.post("/test", cors(), function(req,res,next) {
  const spawn = require("child_process").spawn;
  const process = spawn('python', ["bodyshape.py", "https://res.cloudinary.com/dnsw7cosi/image/upload/v1627983009/gvvidw9o3qoy1mw5yvzf.jpg", 100, 200, 300, false]); 
  process.stdout.on('data', function(data){
      dataToSend = data.toString();
      console.log(data); 
      console.log(dataToSend);
      res.send(dataToSend);
  });

});

module.exports = router;