function resultBmi(){
    var height = document.getElementById('height').value;
    var weight = document.getElementById('weight').value;
    var bmi = document.getElementById('bmi');
    var resultBmi = weight / ((height/100) * (height/100));
    resultBmi = resultBmi.toFixed(1);
    bmi.value = resultBmi;
}

function resultPercentFat(){
    var weight = document.getElementById('weight').value;
    var fat = document.getElementById('fat').value;
    var percent_fat = document.getElementById('percent_fat');
    var resultPercent_fat = (fat / weight) * 100;
    resultPercent_fat = resultPercent_fat.toFixed(1);
    percent_fat.value = resultPercent_fat;
}