from flask import Blueprint, render_template, request
from collections import OrderedDict
from utils import fetch_data, smart_capitalize

doc_who_bp = Blueprint("doc_who", __name__)

@doc_who_bp.route("/doc-who", methods=["GET","POST"])
def doc_who():
    episode_name = ''
    media_type= ''
    scraper_info = {}

    if request.method == "POST":
        episode_name = smart_capitalize(request.form.get("episode"))
        media_type = request.form.get("media_type")

        data = fetch_data(episode_name,media_type)
        if data[0] == 'N/A':
            scraper_info = {"Error": "No data found. Check spelling."}
            return render_template("doc-who.html", scraper_info=scraper_info, episode_name=episode_name, media_type=media_type)

        season, parts, doctor, main_character, companions, featuring, enemy, writer, director = data
        doctor, main_character = ((doctor, []) if doctor else ([], main_character))

        scraper_info = OrderedDict()
        scraper_info["Episode Name"] = episode_name
        scraper_info["Season"] = ", ".join(season) if season else "N/A"
        scraper_info["Number of Parts"] = parts if parts else "N/A"
        if doctor:
            scraper_info["Doctor(s)"] = ", ".join(doctor)
        elif main_character:
            scraper_info["Main Character(s)"] = ", ".join(main_character)
        scraper_info["Companion(s)"] = ", ".join(companions) if companions else "N/A"
        scraper_info["Featuring"] = ", ".join(featuring) if featuring else "N/A"
        scraper_info["Main Enemy"] = ", ".join(enemy) if enemy else "N/A"
        scraper_info["Writer(s)"] = ", ".join(writer) if writer else "N/A"
        scraper_info["Director(s)"] = ", ".join(director) if director else "N/A"

    return render_template("doc-who.html", scraper_info=scraper_info, episode_name=episode_name, media_type=media_type)