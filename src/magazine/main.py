from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from .models import Subscription, User, Magazine, Plan
from .schemas import UserLogin, UserCreate, PasswordChange, SubscriptionCreate, SubscriptionUpdate, MagazineCreate
from .db import get_db
from .auth import verify_password, get_password_hash
from fastapi import Depends
from sqlalchemy.orm import Session

app = FastAPI(title="Research Assignment",
              version="0.0.1",
              docs_url="/documentation/"
              )

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return JSONResponse(content={"message": "Application is up!"})


@app.post("/login")
def login(request: UserLogin, db:Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == request.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        else:
            raise HTTPException(status_code=401, detail="Invalid username")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/register")
def register(request: UserCreate, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(username=request.username, email=request.email, password=get_password_hash(request.password))
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}
    

@app.post("/change-password")
def change_password(request: PasswordChange, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hased_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@app.post("/logout")
def logout():
    return {"message": "Logout successful"}


@app.post("/subscriptions")
def create_subscription(subscription: SubscriptionCreate, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == subscription.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sub_plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not sub_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    sub_magazine = Subscription(magazine_id=subscription.magazine_id, 
                                user_id=subscription.user_id, 
                                plan_id=subscription.plan_id, 
                                price=sub_plan.price, 
                                renewal_date=datetime.now() + timedelta(days=sub_plan.renewalPeriod), 
                                is_active=True)
    db.add(sub_magazine)
    db.commit()
    db.refresh(sub_magazine)
    return {"message": "Subscription created successfully"}



@app.get("/subscriptions/{user_id}")
def get_subscriptions(user_id: int, db:Session = Depends(get_db)):
    user_subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    if not user_subscriptions:
        raise HTTPException(status_code=404, detail="User not found")
    return user_subscriptions

@app.put("/subscriptions/{subscription_id}")
def modify_subscription(subscription_id: int, subscription: SubscriptionUpdate, db:Session = Depends(get_db)):
    user_subscriptions = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if user_subscriptions:
        # Deactivate the current subscription
        subscription.is_active = False
        db.commit()
        db.refresh(subscription)
    
        new_sub = Subscription(magazine_id=subscription.magazine_id, 
                            user_id=subscription.user_id, 
                            plan_id=subscription.plan_id, 
                            price=subscription.price, 
                            renewal_date=datetime.now() + timedelta(days=30), 
                            is_active=subscription.is_active)
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        return new_sub    
    return None

@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, db:Session = Depends(get_db)):
    user_subscriptions = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if user_subscriptions:
        user_subscriptions.is_active = False
        db.commit()
        return {"message": "Subscription deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")

@app.post("/magazines/create")
def create_magazine(magazine: MagazineCreate, db:Session = Depends(get_db)):
    existing_magazine = db.query(Magazine).filter(Magazine.title == magazine.title).first()
    if existing_magazine:
        raise HTTPException(status_code=400, detail="Magazine already exists")
    
    new_magazine = Magazine(title=magazine.title, description=magazine.description, price=magazine.price, discount=magazine.discount)
    db.add(new_magazine)
    db.commit()
    db.refresh(new_magazine)
    return new_magazine

@app.get("/magazines")
def list_magazines(db:Session = Depends(get_db)):
    magazines = db.query(Magazine).all()
    return magazines


@app.put("/magazines/{magazine_id}")
def update_magaizne(magazine_id: int, magazine: MagazineCreate, db:Session = Depends(get_db)):
    existing_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not existing_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    existing_magazine.title = magazine.title
    existing_magazine.description = magazine.description
    existing_magazine.price = magazine.price
    existing_magazine.discount = magazine.discount
    db.commit()
    return existing_magazine

@app.delete("/magazines/{magazine_id}")
def delete_magazine(magazine_id: int, db:Session = Depends(get_db)):
    existing_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not existing_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    db.delete(existing_magazine)
    db.commit()
    return {"message": "Magazine deleted successfully"}


@app.post("/plans")
def create_plans(plan: Plan, db:Session = Depends(get_db)):
    existing_plan = db.query(Plan).filter(Plan.title == plan.title).first()
    if existing_plan:
        raise HTTPException(status_code=400, detail="Plan already exists")
    new_plan = Plan(title=plan.title, description=plan.description, renewalPeriod=plan.renewalPeriod, tier=plan.tier, discount=plan.discount)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@app.get("/plans/{plan_id}")
def get_plan(plan_id: int, db:Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.put("/plans/{plan_id}")
def update_plan(plan_id: int, plan: Plan, db:Session = Depends(get_db)):
    existing_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    existing_plan.title = plan.title
    existing_plan.description = plan.description
    existing_plan.renewalPeriod = plan.renewalPeriod
    existing_plan.tier = plan.tier
    existing_plan.discount = plan.discount
    db.commit()
    return existing_plan

@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db:Session = Depends(get_db)):
    existing_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(existing_plan)
    db.commit()
    return {"message": "Plan deleted successfully"}

