from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, JobCategory, StuffCategory, SpaceCategory, JobPost, StuffPost, SpacePost

from random import randint

engine = create_engine('sqlite:///gregslist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
admin_user = User(name="Robo Admin", email="robo_admin@gregslist.com",
             picture='static/images/robo_admin.jpg')
session.add(admin_user)
session.commit()

this_user = session.query(User).filter_by(email="robo_admin@gregslist.com").one()

# Create jobs categories and job posts

job_categories = ["finance", "office", "art", "science", "retail", "software", "media", "web", "government", "legal", "marketing", "service"]
dummy_jobs = ["Bailiff", "Horticulturalist", "Radio presenter", "Dressmaker", "Social worker", "Anthropologist", "Car dealer", "Tour guide", "Speech therapist", "Bookmaker", "Comedian", "Garden designer", "Plumber"]
description = "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia."

for job_cat in job_categories:
    category = JobCategory(name=job_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(JobCategory).filter_by(name=job_cat).one()

    print new_cat.name

    for job in dummy_jobs:
        title = job + " " + job_cat + " worker"
        pay = "$" + str(randint(7,100)) + ".00"
        hours = str(randint(5,40))
        job_post = JobPost(title=title,
                           description=description,
                           pay=pay,
                           hours=hours,
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(job_post)
        session.commit()


print "\n\njobs added!\n\n"


stuff_categories = ["antiques", "appliances", "arts+crafts", "atv/utv/sno", "auto parts", "baby+kid", "barter", "beauty+hlth", "bikes", "boats", "books", "business", "cars+trucks", "cds/dvd/vhs", "cell phones", "clothes+acc", "collectibles", "computers", "electronics", "farm+garden", "free", "furniture", "garage sale", "general", "heavy equip", "household", "jewelry", "materials", "motorcycles", "music instr", "photo+video", "rvs+camp", "sporting", "tickets", "tools", "toys+games", "trailers", "video gaming", "wanted"]
dummy_stuff = ["Dinosaur bookends, handmade", "Edmund Scientific Astroscan Telescope", "Fish", "Meter Valve Box", "Parrot Bird Cage ", "Hangar Doors", "Pink, red and white felt flower wreath", "Colorfully rustic, wallhanging candle holders", "Gold painted, rustic wood with mason jar vase", "Three little kittens, no mittens", "Liberty Gun Safe - Presidential Series 50", "Tow Car Shield", "Traeger BBQ/Smoker, cover, tray, 6 bags of pellets", "5 Ton Fridgidaire High Efficiency Air Conditioner AC With 5 Ton Coil", "Pottery Barn Lina Moroccan Pillows", "3.5 Ton Fridgidaire High Efficiency Air Conditioner / W/ 3.5 Ton Coil", "Pottery Barn Jewelry Box ", "Creative Memories Shape Punchers", "Shipping Container Cover for Storage Containers(container)", "Various types of large-volume, plastic or steel containers for liquids</", "Rustic handmade display shelf with 'built in' planter", "Rare! Converse airline / bowling bag style AND pink 'clutch'", "FOR SALE PROPERTY 1.89 Acres w/Panoramic Views-Older HomeOutdoor Light Fixture, Marine Quality, Heavy Duty", "Staple Pliers lot of 3", "Star Wars metal spaceships / starships (Hot Wheels brand)Star Wars Tie Fighter and Ghost ship set, metal (Hot Wheels brand)", "*Solid* *Wood* *Picture* *Window* *Wood* *Picture* *Window* - $80Fish Tank 34 Gal. With Orniments", "Faded green, handmade, Welcome sign with mason jar", "Garage storage cabinet cabinetsEagle Creek Cargo Switchback Plus Wheeled Luggage  $70", "Coleman firepit grill $39   ", "Full metal fidget spinners, matte black", "Old tools", "woodworking stuff", "dabs!", "Stainless steel Bird cages    ", "Maxi cosi car seat    ", "BioLite Wood Burning CampStove First Generation", "Greek style columnar brass candle holders", "Solidex 928xt VHS video tape rewinder", "Vitamix 3600 blender  ", "Canon MF8280CW Printer", "TX RACING WHEEL XBOX  ", "Balinese dancers framed watercolor painting $29", "Biolight stove", "Harman kardon HKTS 16BQ", "Optoma Technology DH1011 Full HD DLP 3D Projector", "WALKER<span cl", "stuff not using  ", "QUICKIE ELECTRIC WHEELCHAIR   ", "Atmomixani Nemesis Mechanical Vape Mod, Atmo Dome", "SERTA 3000 Perfect Sleeper king size double pillow mattress", "DAKOTA MENS LARGE WATERPROOF JACKET / COAT", "10 Ton Manual Log Splitter with Polls", "SERTA 3000 Perfect Sleeper king size double pillow mattress", "Vintage HAM Radio Set up--everything but the tower!", "Aquarium Bio Filter   ", "Garden Umbrella Stand ", "Polar Loop Activity Tracker Black", "ZBOARD", "1979 ATC 110 frame / rear end back axles", "Studio Sale TODAY ONLY! - SONY 32'' Flat Screen TV", "barn-art memorabelia barn art barnart", "nordic track CX938    ", "Qu@lity TOP SHELF m@riju@n@ delivery available", "Boat-mooring / jet-ski dock / diving-raft with 55-gal, plastic barrels</", "Refrigerator", "Pink Sparkles Barbie Jaguar   ", "Amway Artistry Make up Mirrors", "Wanner Hydra-Cell pumps: for corrosive, abrasive, and hot fluids", "bathroom exhaust fan  ", "Pond stones,rocks,  aquarium ,fish tanks", "6 Rolls of Decorative Mesh    ", "330 gallon, jumbo, food-grade, plastic tanks for rainwater collection", "Pet Ornament", "Set of four Studded Snow Tires", "Water Pik Water Flosser", "RV Paddle Entry Door Lock Latch Handle Deadbolt NEW Camper Trailer", "Sit Stool", "Pole Lamp for Indirect Light  ", "Carpet Cleaning TruckMount   OBO", "French door refrigerator/freezer", "Like NEW Pacific Trail Ladies Middleweight Waterproof Coat", "Utility cargo trailer ", "Pet Carrier for small dog", "Round Brown Table", "LIKE NEW MEDIUM SIZE (30') WIRE DOG KENNEL/CRATE", "2 Mt. St. Helens Climbing Permits August 1st Tuesday", "Build a Bear Sock Monkey ", "Duracell Power Mat for 2 devices", "crocheted small child headwarmer 196", "Crocheted newborn bonnet set  ", "Duracell Power Mat - Portable Charger Set", "2007 Victory Lane Nascar Gold #9 Ornament", "2007 Victory Lane Nascar Gold #24 Ornament", "Dry Ice Fog Machine   ", "2007 Victory Lane Nascar #29 Gold Ornament", "Crocheted pink slouchy 345    ", "TX RACING WHEEL XBOX  ", "Wine Glass Stemware   ", "crocheted adults Broncos inspired sloudy beanie hat", "Halter top<spa", "Newborn bonnet and bootie set ", "Water Glass Stemware  ", "Carpenters - Greatest Hits - Song Book", "Welder<span cl", "Monkees Greatest Hits Song BookCountry Charts Hits song book ", "Mario Kart Game and Book for the Wii", "Fellowes Bankers Box Stor/File Storage Boxes, String &amp; Button", "New BRP Black Motorcycle Helmet Size Small", "Pallet / Warehouse Rack", "Super Mario Bros Game and Book for the Wii", "Pallet / Warehouse Rack", "Kenmore Microwave Oven", "3 New Coleman Coolers ", "Isador Bonheur bronze sculpture.  1960's  Mint Condition"]

for stuff_cat in stuff_categories:
    category = StuffCategory(name=stuff_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(StuffCategory).filter_by(name=stuff_cat).one()

    print new_cat.name

    for thing in dummy_stuff:
        price = "$" + str(randint(1,500)) + ".00"
        stuff_post = StuffPost(title=thing,
                           description=description,
                           price=price,
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(stuff_post)
        session.commit()


print "\n\nstuff added!\n\n"


space_categories = ["apartments", "homes", "office", "parking", "for sale", "rooms", "vacation rentals", "sublets"]
dummy_space = [" Hit the bulls-eye & Rent here! Luxury 1 Bdrm w/ Huge Everything", "Parking Space, One Block Away NW 23RD!! Available 8/1/17 & 9/1/17", "Newly Renovated, Stainless Steel, New Flooring and much more", "Need Extra Space? Dry, secure storage! Avail 08/01/17 Close to NW 23rd", "Don't Gamble on Your Next Place! Win in This 2 Bedroom!", "#259-301 Corner Unit , Extra Storage, W/D, Roommate Friendly !! Pool !", "Creative Office Space in Central Downtown Portland", "Brand New Amenities *FREE MONTH* Clean & Simple MOVE NOW Tigard 97223", "Just One Opportunity Left to Get 1-month Free! New Homes, New Deals", "Great Room feel, hardwoods, large shower, DBL garage-3BR", "Very nice 2-story house in Morning Green Neighborhood in Hillsboro!", "$500 Room by Max Line/Mall 205 - Renting for 2mos ONLY", "Package receiving service, 24-Hour maintenance response, Sundeck", "Carport, Parking with Cover near NW 23RD $175/Mo Available 08/01/2017", "Beautiful two bedroom townhome, newly renovated, community playground", "Need a Summer Retreat APARTMENT AVAILABLE SOON!", "Newly renovated condo right across from the beach for rent!", "Contemporary, Urban 1 bedroom w/ Awesome City View! $1395", "Wood-style flooring, Disability Access, Accepts Electronic Payments", "Italian Porcelain Tile & Custom Wood Cabinetry in a 1x1 Apartment!", "3 bed/2.5 bath Home In Portsmouth Neighborhood", "Brand New 3 Bdrm Townhouse w/ High-End Finishes! Washer/Dryer Incl.!", "TWO BEDROOM IN TIGARD ENJOY PLAYGROUND & POOL ", "Brand New 3 Bdrm Townhouse w/ High-End Finishes! Washer/Dryer Incl.!", "Office Available in Historic Building at 6th & Main", "Newer 4 Bedroom Townhouse-End Unit! High End Finishes!", "Retail Space near SR-500", "3 Bedroom Condo", "Newer 4 Bedroom Townhouse-End Unit! High End Finishes!", "Very Nice Lake Oswego 2-story - includes seasonal yard care!", "Beautiful Ground Floor 2 Bed 1 Bath Flat! Apply Online Today!", "1 Bth. Washer / Dryer . Off Scholls Ferry by Washington sq mall", "Newer 4 Bedroom Townhouse-End Unit! High End Finishes!", "Call For Specials on our One Bedroom Apartment Homes!", "Beautiful newly remodeled 1x1 ready for move-in, pet friendly", "Room for rent in SW Portland near Barbur and Capitol hwy", "***PERFECT 3 BDRM HOME W/BONUS RM**OPEN PLAN**FRPLC**PETS OK+FENCED YD", "Brand New 3 Bedroom Townhouse w/ 2-Car Garage! Washer/Dryer Inc", "Brand New 3 Bedroom, 2.5 Bath Townhome w/ High End Finishes!", "Arbor Lodge/Overlook - Willamette Blvd Townhouse", "GROUND FLOOR 1X1!!! NEW CARPET, W/D INCLUDED, CARPORT!! READY NOW!!", "Lovely Spacious Tigard Home on Bull Mountain!", "Fabulous 'duplex' in quiet ALAMEDA neighborhood. Nice landlady.", "2 bedroom 1.5 bathroom townhouse with washer and dryer!!", "Newly Remodeled 2 Bedroom 1 Bath in St. Helens, $1,500!!", "Spectacular 3 bed 2.5 bath home w/ easy access to I-5", "WOW WELL MANICURED AND MAINTAINED HOME", "Office Best Deal In Town***Move In Ready**Come And See Us", "Stunning 3 bed 2.5 bath Townhome w/ easy access to HWY 26", "Love the location!  Come see our new look!  Move-In Ready!", "** SW Portland Special**            ", "Come see the new look at The Ridge at Mt. Park", "Newer 3 bed 2.5 bath townhome   ", "Finished basement room cool all summer.", "Multi-Level Home with Territorial Views!", "Room and Sunroom with Private Entrance in Peaceful Home.", "*Top Floor, Heated Pool, Sauna, Huge Living Room, Gas Fireplace!!", "Contemporary, Urban 1 bedroom w/ Awesome City View! $1395", "Gorgeous Corner Home! -(A plan) with Panoramic View ! - Huge Closets!", "Tour your new home today! Look and Lease Special!", "Amazing  2 bed, 2 bath 1st floor, wash/dryer Huge Patio TOUR TODAY!!", "Last Retail Space next to I-205 Recently Built!         ", "Expansive bedrooms, Accepts Electronic Payments, Garage Parking", "FOR SALE: Outstanding Remodeled Tigard Townhome!", "'result-price'>$3150", "Grant Park ADU (Furnished)        ", "FOR SALE: Amazing Aloha Tri-Level under $400k!", "Luxury at the Beach (elevator, master suites...much more!)", "FOR SALE: Amazing TransitionalKruse Ridge Home", "Beautiful Vintage Alameda home - Rent includes Yard Care!", "FOR SALE: Gorgeous NW PDX Remodeled Mid-Century        ", "Fully Furnished Office For 6+ & Free HON Furniture  ", "FOR SALE: Your Search is Over, This Cedar Mill Home Has it All!", "FOR SALE: Beautiful Lake Oswego New Construction!", "Eclipse Rental", "FOR SALE: Single Level Living in Beautiful Charbonneau", "FOR SALE:Great Starter Home -$259,900", "FOR SALE: 4 Wheel Drive Business in Gladstone", "FOR SALE: Modern Victorian Masterpiece in the Heart of Wine Country", "START YOUR SUMMER AT THE SPRINGS!! 2 bd/1.5 bath!! SPARKLING POOL!!", "This PERFECT starter home is brand new and full of upgrades! Must See!", "FALL IN  WITH PARC EAST! Apply Today for Your New Home!", "FOR SALE: Charming Cottage on Peaceful 1/3rd Acre", "Gorgeous 2 bed 2 bath home w/ Stainless Appliances", "2bedroom 1bath   HURRY BEFORE IT'S GONE", "Don't Miss Your Opportunity to Make This Amazing Home Yours!!!", "FOR SALE: Lake Oswego New Construction - Still Time to Customize!", "FOR SALE: Charming Home in Magnolia Estates!", "PENTHOUSE, city view, AC, urban interior & HUGE walk-in closet!", "FOR SALE: Spacious 4 Bedroom Home with Double Master Suite-$439,900", "Charming Furn or Unfurn LO cottage - Flexible Lease Inclds Yard Care!", "FOR SALE: Move-In Ready Clackamas Home with a View!", "FOR SALE: Absolutely Adorable Southeast PDX Home!", "FOR SALE: Luxurious Bull Mountain Home", "Pets Allowed, Wood-style flooring, Elevator fed building in SW", "FOR SALE: Lake Oswego Modern Elegance!", "Charming Updated Bungalow with Office & Bonus Room", "FOR SALE: Stunning European Condo with Sweeping Columbia River Views", "Beautiful 2x2 upgraded", "From $104/nt, $567/wk, $2160/mo. @ Vancouver, Wa, close to Portland!", "FOR SALE: Amazing Aloha Townhouse!", "NEW BUILDING ON MISSISSIPPI AVAILABLE NOW 1 AND 2 BEDS", "Additional loft! Great place and great location!", "Awesome Mountain/River Views from this Beautiful One Bed! 6 Weeks Free", "FOR SALE: Remodeled Condo with 2 Car Garage", "Lovely Tigard Home w/ Large Bonus Room!", "From $117/nt, $567/wk or $2160/mo @ Tigard, near Downtown Portland", "Downtown Portland Class A Office   ", "YOU FOUND IT! Attached Garage, Pool, Sauna AND MORE...CALL TODAY !!!", "The Blueberry Patch"]

for space_cat in space_categories:
    category = SpaceCategory(name=space_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(SpaceCategory).filter_by(name=space_cat).one()

    print new_cat.name

    for space in dummy_space:
        price = "$" + str(randint(100,1000000000)) + ".00"
        space_post = SpacePost(title=space,
                           description=description,
                           price=price,
                           street="6666 NW 23rd",
                           city="Portland",
                           state="OR",
                           zip="97210",
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(space_post)
        session.commit()


print "\n\nspace added!\n\n"


