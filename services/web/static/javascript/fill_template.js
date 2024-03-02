const QUESTION_NUMBER = 1;  // <- Change this to set the question number

const embedded_data_value = "value" + QUESTION_NUMBER + "_";  // e.g. value1_1 (last digit is set later)
const embedded_data_rank = "rank" + QUESTION_NUMBER + "_";  // e.g. rank1_1 (last digit is set later)
const embedded_data_error = "error" + QUESTION_NUMBER + "_";  // e.g. error1_1 (last digit is set later)
const embedded_data_person = "person" + QUESTION_NUMBER + "_";  // e.g. person1_1 (last digit is set later)

const xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
        const server_response = JSON.parse(xhttp.responseText);

        console.log(server_response);

        for (var i = 0; i < server_response.length; i++) {
            console.log(i);
            const value_element = document.getElementById("value_" + (i + 1));
            const rank_element = document.getElementById("rank_" + (i + 1));
            const error_element = document.getElementById("error_" + (i + 1));
            const person_element = document.getElementById("person_" + (i + 1))

            const value = server_response[i]['value']
            const rank = server_response[i]['rank']
            const error = server_response[i]['error']
            const person = server_response[i]['person']

            if (value_element != null) {
                Qualtrics.SurveyEngine.setEmbeddedData(embedded_data_value + (i + 1), value);
                value_element.innerHTML = value;
            }

            if (rank_element != null) {
                Qualtrics.SurveyEngine.setEmbeddedData(embedded_data_rank + (i + 1), rank);
                rank_element.innerHTML = rank;
            }

            if (error_element != null) {
                Qualtrics.SurveyEngine.setEmbeddedData(embedded_data_error + (i + 1), error);
                error_element.innerHTML = error;
            }

            if (person_element != null) {
                Qualtrics.SurveyEngine.setEmbeddedData(embedded_data_person + (i + 1), person);
                person_element.innerHTML = person;
            }
        }
    }
}

xhttp.open("GET", "https://c1.elifast.com/query-dataset?question_number=" + QUESTION_NUMBER);
xhttp.send();
