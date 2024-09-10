function getRecommendExercise(event) {
    const selected_recommendexercise = document.getElementsByName('selected_recommendexercise'); //날짜 체크박스
    const muscle = document.getElementsByName('muscle'); //근력운동 체크박스
    const cardio = document.getElementsByName('cardio'); //유산소운동 체크박스
    const time = document.getElementsByName('time'); //운동시간 체크박스
    const health_significants = document.getElementsByName('health_significants'); //부상부위 체크박스

    // 운동 추천 거부시 체크박스 비활성화 코드(if문 전체)
    if (event.target.value == "recommendexercise_no"){
        for (let i = 0; i < selected_recommendexercise.length; i++) {
            selected_recommendexercise[i].disabled = true;
        }

        for (let i = 0; i < muscle.length; i++) {
            muscle[i].disabled = true;
        }

        for (let i = 0; i < cardio.length; i++) {
            cardio[i].disabled = true;
        }

        for (let i = 0; i < time.length; i++) {
            time[i].disabled = true;
        }

        for (let i = 0; i < health_significants.length; i++) {
            health_significants[i].disabled = true;
        }
    }
    // 운동 추천 찬성시 체크박스 활성화 코드(else문 전체)
    else{
        for (let i = 0; i < selected_recommendexercise.length; i++) {
            selected_recommendexercise[i].disabled = false;
        }

        for (let i = 0; i < muscle.length; i++) {
            muscle[i].disabled = false;
        }

        for (let i = 0; i < cardio.length; i++) {
            cardio[i].disabled = false;
        }

        for (let i = 0; i < time.length; i++) {
            time[i].disabled = false;
        }

        for (let i = 0; i < health_significants.length; i++) {
            health_significants[i].disabled = false;
        }
    }
  }

function getRecommendDiet(event){
    const allergy = document.getElementsByName('allergy');
    const selected_recommenddiet = document.getElementsByName('selected_recommenddiet');
    const selected_meal = document.getElementsByName('selected_meal');
    const occupation = document.getElementsByName('occupation');
    const recommensnack = document.getElementsByName('recommendsnack');
    
    if (event.target.value == "recommenddiet_no"){
        for (let i = 0; i < allergy.length; i++) {
            allergy[i].disabled = true;
        }
        for (let i = 0; i < selected_recommenddiet.length; i++) {
            selected_recommenddiet[i].disabled = true;
        }
        for (let i = 0; i < selected_meal.length; i++) {
            selected_meal[i].disabled = true;
        }
        for (let i=0; i< occupation.length; i++){
            occupation[i].disabled = true;
        }
        for (let i=0; i< recommensnack.length; i++){
            recommensnack[i].disabled = true;
        } 
    }
    else{
        for (let i = 0; i < allergy.length; i++) {
            allergy[i].disabled = false;
        }
        for (let i = 0; i < selected_recommenddiet.length; i++) {
            selected_recommenddiet[i].disabled = false;
        }
        for (let i = 0; i < selected_meal.length; i++) {
            selected_meal[i].disabled = false;
        }
        for (let i=0; i< occupation.length; i++){
            occupation[i].disabled = false;
        }
        for (let i=0; i< recommensnack.length; i++){
            recommensnack[i].disabled = false;
        }
    }
}