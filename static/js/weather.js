async function getWeather() {
    const city = document.getElementById("cityInput").value;
    const apikey = "49d3c5cac87c3a5e3a9f272c0626193a"
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${apikey}`;
    
    try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("City not found");
    const data = await res.json();

    const result = `
        <h3>Weather in ${data.name}</h3>
        <p><strong>Temperature:</strong> ${data.main.temp} °C</p>
        <p><strong>Weather:</strong> ${data.weather[0].description}</p>
        <p><strong>Humidity:</strong> ${data.main.humidity}%</p>
        <p><strong>Wind:</strong> ${data.wind.speed} m/s</p>
    `;
    
    document.getElementById("weatherResult").innerHTML = result;
    } catch (error) {
    document.getElementById("weatherResult").innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}