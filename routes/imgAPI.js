const express = require("express");
const router = express.Router();

router.post("/", function (req, res, next) { 
    global.imglink = req.body.datas.link;
});

module.exports=router;