const express = require("express");
const router = express.Router();

router.post("/", function (req, res, next) { 
    imglink = req.body.datas.link;
    console.log(imglink)
});

router.get("/", function(req,res,next) {
    const spawn = require("child_process").spawn;
    console.log(gender);
    const process = spawn('python', ["bodyshape.py", imglink, shoulder, waist, hip, gender]); 
    process.stdout.on('data', function(data){
        console.log(`${data}`); 
        dataToSend = data.toString(); 
        res.send(dataToSend);
    });

});

module.exports=router;