const survey = new Survey.Model(contactjson);
// You can delete the line below if you do not use a customized theme
survey.applyTheme(themeJson);
survey.onComplete.add((sender, options) => {
    console.log(JSON.stringify(sender.data, null, 2));
    saveSurveyResults("https://pythonjson.geodati.fmach.it/", sender.data)
});

function saveSurveyResults(url, json) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify(json)
    })
    .then(response => {
        if (response.ok) {
            $("#formgood").removeAttr('hidden');
            console.log("good")
        } else {
            $("#formbad").removeAttr('hidden');
            console.log("false")
        }
    })
    .catch(error => {
        $("#formbad").removeAttr('hidden');
        console.log("false")
    });
}


$("#surveyElement").Survey({ model: survey });