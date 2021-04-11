// DATA
const data = {{ChartData |safe}};

// OPTIONS
var options = {
        responsive:false, 
        plugins: {
            tooltip:{
                bodyColor: ' 	#191414',
                backgroundColor: 'rgba(155, 155, 155, 0.8)',   
                displayColors : false,
                titleFont: {style: 'bold'},
                

                bodySpacing: 5,
                callbacks :{
                    label: function(context){
                        
                        
                        var index = context.dataIndex;
                        
                        return ['Valence:           ' + context.dataset.data[index].y, 'Danceability:   ' + context.dataset.data[index].x, 'Energy:            ' + + context.dataset.data[index].r];
                    },
                    title: function(context){
                        var index = context[0].dataIndex;
                            
                        return context[0].dataset.data[index].track_name
                    }
                }
            }
        }
            };



var ctx = document.getElementById('ChartAnalysis');



var myChart = new Chart(ctx, {
    type: 'bubble',
    data: data,
    options: options,
    });