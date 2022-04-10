var vl = new Vue ({
    data:{
            hour:0,
            minute:0,
            ms:0,
            second:0,
            time:'',
            str:'00:00:00',
            total_second:0
    },
    

    methods:{

        timeStart(){
        this.time =setInterval(this.timer,50)
        },
        
        timer () {
        this.ms =this.ms +50       
        if (this.ms >=1000) {
        this.ms =0
        this.second =this.second +1       
                }
        if (this.second >=60) {
        this.second =0
                  this.minute =this.minute +1        
                }
        if (this.minute >=60) {
        this.minute =0
                  this.hour =this.hour +1        
                }
    //
    this.str =this.toDub(this.hour) +':' +this.toDub(this.minute) +':' +this.toDub(this.second)
            
            this.total_second = this.hour * 3600 +this.minute*60 +this.second*1
     },
     toDub (n) {
             if (n <10) {
     return '0' + n
     }else {
     return '' + n
     }
     },
     stop () {
     console.log('stop')
     clearInterval(this.time)
     },
     reset () {
     clearInterval(this.time)
     this.minute =0
     this.ms =0
     this.second =0
     this.str ='00:00:00'
     },
     },
     
          
})