from flask import Blueprint, render_template, request
from flask_login import current_user
from datetime import date
from extensions import db
from models import Rowingdata
from utils import permission_required

rowing_bp = Blueprint("rowing", __name__)

@rowing_bp.route("/rowing", methods=["GET","POST"])
def rowing():
    leg_1 = leg_2 = leg_3 = ''
    todays_date = date.today()
    message = None

    if request.method == "POST":
        # Get date from form, fallback to today 
        selected_date_str = request.form.get("rowing_date")
        selected_date = date.fromisoformat(selected_date_str) if selected_date_str else todays_date

        existing_entry = Rowingdata.query.filter_by(user_id=current_user.id, date=selected_date).first()
        if existing_entry:
            message = f"You have already submitted rowing data for {selected_date}. <br> Submitting again will replace it"
            db.session.delete(existing_entry)
            db.session.commit()

        leg_1 = float(request.form.get("leg_1",0))
        leg_2 = float(request.form.get("leg_2",0))
        leg_3 = float(request.form.get("leg_3",0))

        current_entry = Rowingdata(current_user.id, leg_1, leg_2, leg_3,date=selected_date)
        db.session.add(current_entry)
        db.session.commit()

    entries = Rowingdata.query.filter_by(user_id=current_user.id).order_by(Rowingdata.date).all()
    dates = [e.date.strftime("%Y-%m-%d") for e in entries]
    avg_times = [float(e.avg_500m_time_in_secs) for e in entries]

    return render_template("rowing.html", leg_1=leg_1, leg_2=leg_2, leg_3=leg_3,date=todays_date, avg_times=avg_times, dates=dates, message=message)
