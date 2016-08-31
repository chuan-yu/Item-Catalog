from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Items for 'swimming'
category1 = Category(name='swimming')
session.add(category1)
session.commit()

item1 = Item(name='swim cap', category=category1, description="Swim in style with this terrific Speedo Swim Cap. The silicone composition delivers greater elasticity and durability than standard latex caps. This silicone cap delivers a super-soft fit that prevents hair pulling.")
session.add(item1)
session.commit()

item2 = Item(name='goggle', category=category1, description="Unchanged classic fit with soft silicone eye seals. Two-tone silicone double headstrap and ergonomic adjustable clip. Mirrored lens coating helps to reduce glare. Features three interchangeable nose pieces. UV protection. Anti-fog. PVC free. Latex free.")
session.add(item2)
session.commit()

item3 = Item(name='ear plug', category=category1, description="3M personal protective equipment sold through Amazon's Industrial and Scientific Department is only intended for US occupational workplace use. This 3M personal protective equipment must be used in compliance with the Occupational Safety and Health Administration (OSHA) Personal Protective Equipment (PPE) standard (29 CFR 1910.132) and all other applicable health and safety standards, as well as all user instructions, warnings and limitations accompanying each product. It is essential that all product user instructions and government regulations on the use of each product be followed in order for the product to help protect the wearer. Misuse of personal protective equipment may result in injury, sickness, or death. For correct product selection and use, individuals should consult their on-site safety professional or industrial hygienist. For additional product information, visit www.3M.com/PPESafety.")
session.add(item3)
session.commit()

# Items for 'golf'
category2 = Category(name='golf')
session.add(category2)
session.commit()

item1 = Item(name='range finder', category=category2, description="Bushnell Tour v3 Golf Rangefinders Tour v3... FEEL Your Exact Distance! The Bushnell Tour v3 Golf Rangefinder features JOLT Technology, which allows golfers to feel their exact distance with each acquisition. The new technology, combined with new ergonomic design, will eliminate any doubt about yardages and offers the exact distance up to 1,000 yards.Bushnell Tour v3 Rangefinders feature: ")
session.add(item1)
session.commit()

item2 = Item(name='ball', category=category2, description="The new Titleist Pro V1 golf ball is designed for serious golfers of all levels that demand Tour-validated technology and performance. Featuring an improved, higher coverage 392 dimple design, along with a new staggered wave parting line and exclusive A.I.M. (Alignment Integrated Marking) sidestamp, the new Pro V1 golf ball provides long, consistent distance with the driver and long irons, while maintaining soft feel and high performance into and around the green with Drop-And-Stop control.")
session.add(item2)
session.commit()


item3 = Item(name='club set', category=category2, description="A Full Set With A Great Combination Of Distance and Forgiveness Right Out Of The Box. Offers the performance men want for their game and an eye-catching look that suits their style. This set comes with 12 pieces (9 clubs, 2 headcovers, and 1 bag).")
session.add(item3)
session.commit()

# Items for 'badminton's
category3 = Category(name='badminton')
session.add(category3)
session.commit()

item1 = Item(name='racket', category=category3, description="Set includes 2 racquets and 2 nylon shuttlecocks and a case")
session.add(item1)
session.commit()

item2 = Item(name='shuttlecock', category=category3, description="Description:6PCS White Feather Shuttlecocks Badminton.This Feather Shuttlecocks combine useful value and recreational value into a single unit.Set of six official size and weight shuttlecocks.Enables fast volleys and ensures flight consistency.Package content:6PCS Badmintons")
session.add(item2)
session.commit()
