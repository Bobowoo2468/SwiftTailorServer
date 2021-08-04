const express = require("express");
const router = express.Router();

router.get("/", function(req,res,next) {
    const spawn = require("child_process").spawn;
    const process = spawn('python', ["bodyshape.py", imglink, shoulder, waist, hip, gender]); 
    process.stdout.on('data', function(data){
        dataToSend = data.toString(); 
        res.send(dataToSend);
    });

});

module.exports=router;