
function submitit() {

  removeAll();

  let text = document.getElementById("mist").value;
  let text2 = JSON.stringify(text);
  //console.log(text);
  fetch('http://localhost:8000/mist/'+text,
  {
    method: "GET",
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseData) => {
    let response = responseData;
    myPrint(response);
    return responseData;
  })
  .catch(error => console.warn(error));

}

function removeAll(){
  let div1 = document.getElementById('display-stance');
  while (div1.firstChild) {
    div1.removeChild(div1.firstChild);
  }
  let div2 = document.getElementById('display-mist');
  while (div2.firstChild) {
    div2.removeChild(div2.firstChild);
  }
}

function myPrint(response)
{
  let max = -1, mText = '';
  for(let mist in response){
    let value = response[mist];
    console.log(value);
    if(value.stance === 'Accept'){
      if(max < value.prob[1]){
        max = value.prob[1];
        mText = value.text;
      }
    } 
  }
  console.log('Max is: ' + max);
  console.log('Max Tweet is: ' + mText);

  generateResults(max,mText);

}

function generateResults(max, mtext){

  if(max != -1){
    //stance
    let disStance1 = document.createElement('h2');
    disStance1.setAttribute(
      'style',
      'color: green; font-size: 40px;'
    );
    disStance1.append("Accept");
    let div1 = document.getElementById('display-stance');
    div1.appendChild(disStance1);
    //mist
    let disStance2 = document.createElement('h2');
    disStance2.append(mtext);
    let div2 = document.getElementById('display-mist');
    div2.appendChild(disStance2);
  }
  else{
    //stance
    let disStance1 = document.createElement('h2');
    disStance1.setAttribute(
      'style',
      'color: red; font-size: 40px'
    );
    disStance1.append("Reject");
    let div1 = document.getElementById('display-stance');
    div1.appendChild(disStance1);
    //mist
    let disStance2 = document.createElement('h2');
    disStance2.append("The tweet entered does not contain any misinformation regarding COVID 19 vaccines.");
    let div2 = document.getElementById('display-mist');
    div2.appendChild(disStance2);
  }
}


