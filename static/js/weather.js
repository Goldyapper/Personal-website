document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("cityInput");  //get the city id from the page
    const button = document.getElementById("getWeatherButton");
    const result = document.getElementById("weatherResult");

    // Handle clicking the button
    button.addEventListener("click", getWeather);

    // Handle pressing Enter while in the input box
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault(); // Stop form or browser default action
            getWeather();
        }
    });

    async function getWeather() {
        const city = input.value.trim();
        const apiKey = "49d3c5cac87c3a5e3a9f272c0626193a" //api key that i have generated
        
        if (!city) {
            result.innerHTML = `<p style="color:red;">Please enter a city name.</p>`;
            return;
        }

        const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&units=metric&appid=${apiKey}`;
        result.innerHTML = `<p>Loading...</p>`;//this shows the user that the website is loading infomation

        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error("City not found");//makes sures that the user typed in a correct city
            
            const data = await res.json();
            const time = new Date().toLocaleTimeString();

            const result = ` 
                <h3>Weather in ${data.name} at ${time} </h3>
                <p><strong>Temperature:</strong> ${data.main.temp} °C</p>
                <p><strong>Weather:</strong> ${data.weather[0].main}</p>
                <p><strong>Humidity:</strong> ${data.main.humidity}%</p>
                <p><strong>Wind:</strong> ${data.wind.speed} m/s</p>
            `;//pulls relevant info

            document.getElementById("weatherResult").innerHTML = result;//return the results
        } catch (error) {
            document.getElementById("weatherResult").innerHTML = `<p style="color:red;">Error: ${error.message}</p>`; //error mesage if the city is wrong
        }
    }
});