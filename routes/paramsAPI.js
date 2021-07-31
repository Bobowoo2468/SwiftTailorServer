const express = require("express");
const router = express.Router();

router.post('/', function (req, res, next) { 
    global.shoulder = 500 - req.body.data.sheight;
    global.waist = 500 - req.body.data.wheight;
    global.hip = 500 - req.body.data.hheight;
    global.gender = req.body.data.gender;
});

module.exports = router;
