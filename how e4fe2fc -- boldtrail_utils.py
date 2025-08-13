[33mcommit e4fe2fc2111e8a0d9c50fcf86667148b2e26c05d[m
Author: antarahleet <antarahleet@gmail.com>
Date:   Thu Aug 7 11:00:38 2025 -0400

    Fix: Update BoldTrail login to handle multi-step authentication

[1mdiff --git a/cache/downloads/boldtrail_upload.csv b/cache/downloads/boldtrail_upload.csv[m
[1mnew file mode 100644[m
[1mindex 0000000..f7aef88[m
[1m--- /dev/null[m
[1m+++ b/cache/downloads/boldtrail_upload.csv[m
[36m@@ -0,0 +1,10090 @@[m
[32m+[m[32mfirst_name,last_name,status,deal_type,email_optin,text_on,phone_on,email,cell_phone_1,primary_address,primary_city,primary_state,primary_zip,agent_notes[m
[32m+[m[32mBrett,Devincent,New Lead,Seller,yes,yes,yes,,6179670302,6 Russell Trufant Rd,"Carver, Ma",MA,02330,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 6442af946663d755407ea247[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Cancelled[m
[32m+[m[32m* property address: 6 Russell Trufant Rd[m
[32m+[m[32m* property city: Carver, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02330[m
[32m+[m[32m* name: Brett Devincent[m
[32m+[m[32m* name 2: Sabrina Roy[m
[32m+[m[32m* mls name: John Paige[m
[32m+[m[32m* mls name 2: Amanda Paige[m
[32m+[m[32m* phone: 617-967-0302[m
[32m+[m[32m* phone status: DNC[m
[32m+[m[32m* phone 2: 508-455-1827[m
[32m+[m[32m* phone 3: 508-641-2938[m
[32m+[m[32m* address: 6 Russell Trufant, Carver, Ma, MA 02330[m
[32m+[m[32m* address 2: 6 Russell Trufant Rd, Carver, Ma, MA 02330[m
[32m+[m[32m* first name: Brett[m
[32m+[m[32m* last name: Devincent[m
[32m+[m[32m* mailing street: 6 Russell Trufant Rd[m
[32m+[m[32m* mailing city: Carver[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 02330[m
[32m+[m[32m* list date: 07-17-2025[m
[32m+[m[32m* list price: 699900[m
[32m+[m[32m* days on market: 20[m
[32m+[m[32m* lead date: 04-21-2023[m
[32m+[m[32m* expired date: 06-22-2023[m
[32m+[m[32m* status date: 08-06-2025[m
[32m+[m[32m* listing agent: Karen Lopez[m
[32m+[m[32m* listing broker: Great Estates Realty, Inc.[m
[32m+[m[32m* mls/fsbo id: 73406008[m
[32m+[m[32m* bedrooms: 4[m
[32m+[m[32m* bathrooms: 3[m
[32m+[m[32m* type: SF[m
[32m+[m[32m* year built: 1975[m
[32m+[m[32m* lot size: 0.52[m
[32m+[m[32m* remarks: Warm and spacious Colonial in Carver, MA. Welcome to this beautifully maintained 4-bedroom, 2.5 bathroom home nestled on a private lot. From cozy evenings by the pellet stove to the functional elegance of three floors of living space, this home offers comfort, charm ad versatility. Finished basement ideal for a family room, play area gym, whatever your needs may be. The private fourth floor bedroom on the third level features a full bath and direct access to attic storage  With its welcoming character and flexible living space, this home is ready for its new owners.  Whether your hosting holidays, enjoying quiet weekends, spending time with friends and family this house has the space you need.[m
[32m+[m[32m* agent remarks: 24 hour notice to show, pets on premises. Agent related to seller.[m
[32m+[m[32m* house number: 6[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73406008&o=&n=0[m
[32m+[m[32m* tax id: CARVM40P8E3"[m
[32m+[m[32mBeatrice,Lt,New Lead,Seller,yes,yes,yes,,5086768910,65 Alden St,"Fall River, Ma",MA,02723,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 64d74e4bf45ed62ec7bfbb9b[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 65 Alden St[m
[32m+[m[32m* property city: Fall River, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02723[m
[32m+[m[32m* name: Beatrice Lt[m
[32m+[m[32m* mls name: Beatrice a Mendes Lt[m
[32m+[m[32m* phone: 508-676-8910[m
[32m+[m[32m* phone 2: 508-676-9710[m
[32m+[m[32m* address: 65 Alden St, Fall River, Ma, MA 02723[m
[32m+[m[32m* address 2: 65 Alden St, Fall River, Ma, MA 02723[m
[32m+[m[32m* first name: Beatrice[m
[32m+[m[32m* last name: Lt[m
[32m+[m[32m* mailing street: 100 Eastern Ave[m
[32m+[m[32m* mailing city: Fall River[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 02723[m
[32m+[m[32m* list date: 08-22-2024[m
[32m+[m[32m* list price: 329900[m
[32m+[m[32m* days on market: 346[m
[32m+[m[32m* lead date: 08-12-2023[m
[32m+[m[32m* expired date: 08-05-2025[m
[32m+[m[32m* status date: 08-05-2025[m
[32m+[m[32m* listing agent: Kenneth A Mongeon[m
[32m+[m[32m* listing broker: KAM Realty[m
[32m+[m[32m* mls/fsbo id: 73280902[m
[32m+[m[32m* type: CI[m
[32m+[m[32m* year built: 1871[m
[32m+[m[32m* lot size: 0.25[m
[32m+[m[32m* remarks: This """"Diamond in the Rough"""" granite warehouse is surrounded by luxury apartments!!    Exposed interior trusses, high ceilings, and exposed granite.    Would make a fantastic European Style Cafe and Coffee Shop.  Captured audience surrounds you![m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 65[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73280902&o=&n=0[m
[32m+[m[32m* tax id: FALLM0J27B0000L0010"[m
[32m+[m[32mThomas,Cox,New Lead,Seller,yes,yes,yes,,7815455870,50 Whitehead Ave U:B,"Hull, Ma",MA,02045,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 681097a99efb01a6f5a65a84[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 50 Whitehead Ave U:B[m
[32m+[m[32m* property city: Hull, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02045[m
[32m+[m[32m* name: Thomas Cox[m
[32m+[m[32m* name 2: Barbara Cox[m
[32m+[m[32m* mls name: Barbara Cox[m
[32m+[m[32m* mls name 2: Thomas F Cox[m
[32m+[m[32m* phone: 781-545-5870[m
[32m+[m[32m* phone status: DNC[m
[32m+[m[32m* phone 2: 781-545-2089[m
[32m+[m[32m* phone 2 status: DNC[m
[32m+[m[32m* phone 3: 781-545-4218[m
[32m+[m[32m* phone 3 status: DNC[m
[32m+[m[32m* phone 4: 781-801-3451[m
[32m+[m[32m* address: 50 Whitehead Ave U:b, Hull, Ma, MA 02045[m
[32m+[m[32m* address 2: 50 Whitehead Ave U:b, Hull, Ma, MA 02045[m
[32m+[m[32m* first name: Thomas[m
[32m+[m[32m* last name: Cox[m
[32m+[m[32m* mailing street: 15 Shoal Water Rd[m
[32m+[m[32m* mailing city: Scituate[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 02066[m
[32m+[m[32m* list date: 05-25-2025[m
[32m+[m[32m* list price: 498900[m
[32m+[m[32m* days on market: 8[m
[32m+[m[32m* lead date: 04-29-2025[m
[32m+[m[32m* expired date: 08-05-2025[m
[32m+[m[32m* status date: 08-05-2025[m
[32m+[m[32m* listing agent: Kiowe Smith[m
[32m+[m[32m* listing broker: Barros Realty Trust, LLC[m
[32m+[m[32m* mls/fsbo id: 73379727[m
[32m+[m[32m* bedrooms: 2[m
[32m+[m[32m* bathrooms: 1[m
[32m+[m[32m* type: CC[m
[32m+[m[32m* year built: 1910[m
[32m+[m[32m* lot size: 0.04[m
[32m+[m[32m* remarks: Small Single Family house. NO HOA FEES!  GREAT CONDO ALTERNATIVE. NO FLOOD INSURANCE!    Vinyl sided and small yard for low maintenance. PRICED TO SELL!  Welcome this summer with your New house by the Beach.  A great condo alternative you can enjoy all year round!  3 minute walk to Nantasket Beach, surf shops, boutique shops and restaurants. Stroll down whitehead and across street see """"Lot A"""" huge Beach parking lot for extra guest and your access as a resident. Surf rentals or paddle boards or just stroll on to majestic beach. Minutes to commuter train or Ferry to Boston.  Views of the Boston skyline, Nantasket beach, World?s End, and the bay from the second floor. Potential for a second floor deck off bedroom (*see next door*).  Small bonus room, will make a great office. Interior freshly painted.  New kitchen with quartz countertops, and new appliances. Flooring has been replaced both first and second floors. Bathroom redesigned with marble flooring. Just waiting for your charm added[m
[32m+[m[32m* agent remarks: Email all offers to obijr99@yahoo.com or text 508-740-0813 with any questions. *Buyer and buyers agent do your own due diligence.[m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 50[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73379727&o=&n=0[m
[32m+[m[32m* tax id: HULLM00029P00106"[m
[32m+[m[32mAwem,Realty Llc,New Lead,Seller,yes,yes,yes,,5082780894,38 William Ward St,"Uxbridge, Ma",MA,01569,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 68172fee4417217ce2aa5d93[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 38 William Ward St[m
[32m+[m[32m* property city: Uxbridge, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 01569[m
[32m+[m[32m* name: Awem Realty Llc[m
[32m+[m[32m* mls name: Awem Realty Llc[m
[32m+[m[32m* phone: 508-278-0894[m
[32m+[m[32m* phone status: DNC[m
[32m+[m[32m* phone 2: 508-883-4168[m
[32m+[m[32m* phone 2 status: DNC[m
[32m+[m[32m* address: 38 William Ward St, Uxbridge, Ma, MA 01569[m
[32m+[m[32m* first name: Awem[m
[32m+[m[32m* last name: Llc[m
[32m+[m[32m* mailing street: 38 William Ward St[m
[32m+[m[32m* mailing city: Uxbridge[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 01569[m
[32m+[m[32m* list date: 05-02-2025[m
[32m+[m[32m* list price: 519000[m
[32m+[m[32m* days on market: 95[m
[32m+[m[32m* lead date: 05-04-2025[m
[32m+[m[32m* expired date: 08-05-2025[m
[32m+[m[32m* status date: 08-05-2025[m
[32m+[m[32m* listing agent: Hisham Loji[m
[32m+[m[32m* listing broker: Keller Williams Realty Boston South West[m
[32m+[m[32m* mls/fsbo id: 73368997[m
[32m+[m[32m* bedrooms: 3[m
[32m+[m[32m* bathrooms: 1[m
[32m+[m[32m* type: SF[m
[32m+[m[32m* year built: 1955[m
[32m+[m[32m* lot size: 0.37[m
[32m+[m[32m* remarks: Welcome to this beautifully renovated single-family Ranch located on a quiet dead-end street! This detached home offers 3 spacious bedrooms and 1 full bathroom, thoughtfully designed to maximize every inch of space. The bright eat-in kitchen features gleaming wood floors, brand new appliances including an electric range and refrigerator, and plenty of room for family gatherings. The fully finished basement expands the living space, complete with a game room, bonus room, and a designated laundry area with washer/dryer hookups?ideal for modern living. Enjoy the convenience of 4 off-street parking spaces and an attached 1-car garage. This home has been fully updated, including a brand new septic system designed for 3 bedrooms, ensuring peace of mind for years to come. With two front doors and true move-in condition, this charming home blends functionality and comfort perfectly. Please note: Some photos have been virtually staged to help you envision the home's potential. Must See.[m
[32m+[m[32m* agent remarks: Accompanied showing only. Please use the disposable shoes covers provided at the front door.[m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 38[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73368997&o=&n=0[m
[32m+[m[32m* tax id: UXBRM012AB0739L00000"[m
[32m+[m[32mSampson,L,New Lead,Seller,yes,yes,yes,,7746335486,233 West Mountain Street,"Worcester, Ma",MA,01606,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 68415f39f4c213d49e8e8409[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 233 West Mountain Street[m
[32m+[m[32m* property city: Worcester, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 01606[m
[32m+[m[32m* name: Sampson L[m
[32m+[m[32m* mls name: Sampson Ricky L[m
[32m+[m[32m* mls name 2: Sampson Kelly L[m
[32m+[m[32m* phone: 774-633-5486[m
[32m+[m[32m* phone 2: 508-853-5749[m
[32m+[m[32m* phone 2 status: DNC[m
[32m+[m[32m* address: 233 West Mountain Street, Worcester, Ma, MA 01606[m
[32m+[m[32m* first name: Sampson[m
[32m+[m[32m* last name: L[m
[32m+[m[32m* mailing street: 235 W Mountain St[m
[32m+[m[32m* mailing city: Worcester[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 01606[m
[32m+[m[32m* list date: 06-04-2025[m
[32m+[m[32m* list price: 779900[m
[32m+[m[32m* days on market: 18[m
[32m+[m[32m* lead date: 06-05-2025[m
[32m+[m[32m* expired date: 08-05-2025[m
[32m+[m[32m* withdrawn date: 06-22-2025[m
[32m+[m[32m* status date: 08-05-2025[m
[32m+[m[32m* listing agent: Ricky Sampson[m
[32m+[m[32m* listing broker: Sure Realty[m
[32m+[m[32m* mls/fsbo id: 73385659[m
[32m+[m[32m* bedrooms: 4[m
[32m+[m[32m* bathrooms: 3[m
[32m+[m[32m* type: SF[m
[32m+[m[32m* year built: 2025[m
[32m+[m[32m* lot size: 0.21[m
[32m+[m[32m* remarks: BRAND NEW CONSTRUCTION! This quality built home features 4 bedrooms, 2 1/2 baths, a custom built kitchen, huge living room with gas fireplace, oak hardwoods throughout home, a bonus family room, quartz counters in kitchen and baths, and a very convenient 2nd floor laundry room.This home is located just minutes from I-190 ramp for easy commuting yet offers a spacious backyard with oversized Trex deck for outside entertaining. Builder on site from 12:00 - 2:00 this week - Tuesday through Saturday, stop in and take a tour[m
[32m+[m[32m* agent remarks: contact Rick at 774-239-7136 for all showings[m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 233[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73385659&o=&n=0[m
[32m+[m[32m* tax id: WORCM49B019L0004A"[m
[32m+[m[32mBabita,Rai,New Lead,Seller,yes,yes,yes,,5088891866,297 Lindsey,"Fall River, Ma",MA,02720,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 68172fc14417217ce2aa59f6[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 297 Lindsey[m
[32m+[m[32m* property city: Fall River, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02720[m
[32m+[m[32m* name: Babita Rai[m
[32m+[m[32m* name 2: Sumit Chauhan[m
[32m+[m[32m* mls name: Sumit K Chauhan[m
[32m+[m[32m* mls name 2: Babita Rai[m
[32m+[m[32m* phone: 508-889-1866[m
[32m+[m[32m* phone status: DNC[m
[32m+[m[32m* phone 2: 617-682-5807[m
[32m+[m[32m* phone 3: 508-675-5821[m
[32m+[m[32m* phone 3 status: DNC[m
[32m+[m[32m* phone 4: 774-930-5014[m
[32m+[m[32m* phone 5: 508-259-8038[m
[32m+[m[32m* phone 5 status: DNC[m
[32m+[m[32m* address: 297 Lindsey, Fall River, Ma, MA 02720[m
[32m+[m[32m* first name: Babita[m
[32m+[m[32m* last name: Rai[m
[32m+[m[32m* mailing street: 26 Fremont Ave[m
[32m+[m[32m* mailing city: Everett[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 02149[m
[32m+[m[32m* list date: 05-02-2025[m
[32m+[m[32m* list price: 945000[m
[32m+[m[32m* days on market: 94[m
[32m+[m[32m* lead date: 05-04-2025[m
[32m+[m[32m* expired date: 08-04-2025[m
[32m+[m[32m* status date: 08-04-2025[m
[32m+[m[32m* listing agent: Henry Alfonso[m
[32m+[m[32m* listing broker: Alfonso Realty Co.[m
[32m+[m[32m* mls/fsbo id: 73368617[m
[32m+[m[32m* bedrooms: 4[m
[32m+[m[32m* bathrooms: 7[m
[32m+[m[32m* type: MF[m
[32m+[m[32m* year built: 1900[m
[32m+[m[32m* lot size: 0.13[m
[32m+[m[32m* remarks: Great  investment Opportunity! Commercial and Residential Properties You're considering investing in a unique property with great growth potential. Location: Overlooking Taunton River and historic park in Fall River, with a new commuter train service to Boston. Residential rental units and potential for additional units.- Units:1/1 Bedroom, 3/2 bedrooms, and 1/3 bedrooms, with four units currently rented and one three bedrooms unit vacant.- Parking :2-stall garage and 2-3 off-street parking spaces.- Commercial Space approximately 2,442 sq. ft. of rental space on the bottom street level, potentially for storage, apartments, offices, or retail.- Rental  Commercial Building109 George St, with a newly opened bakery (JJ Bakery) and 1,248 sq. ft. of space, including a walk-in cooler. Vacant unit available for showing immediately. Don't miss this fantastic opportunity for investors and owner occupants![m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 297[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73368617&o=&n=0[m
[32m+[m[32m* tax id: FALLM0S14B0000L0006"[m
[32m+[m[32m481,Bedford Llc,New Lead,Seller,yes,yes,yes,,5082790900,481 Bedford St U:1,"Bridgewater, Ma",MA,02324,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 682a463c4a3157302173ef01[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Cancelled[m
[32m+[m[32m* property address: 481 Bedford St U:1[m
[32m+[m[32m* property city: Bridgewater, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02324[m
[32m+[m[32m* name: 481 Bedford Llc[m
[32m+[m[32m* mls name: 481 Bedford Llc[m
[32m+[m[32m* phone: 508-279-0900[m
[32m+[m[32m* phone 2: 617-759-0207[m
[32m+[m[32m* phone 3: 774-766-2903[m
[32m+[m[32m* phone 3 status: DNC[m
[32m+[m[32m* phone 4: 508-697-8899[m
[32m+[m[32m* phone 4 status: DNC[m
[32m+[m[32m* address: 481 Bedford St U:1, Bridgewater, Ma, MA 02324[m
[32m+[m[32m* first name: 481[m
[32m+[m[32m* last name: Llc[m
[32m+[m[32m* mailing street: 481 Bedford St[m
[32m+[m[32m* mailing city: Bridgewater[m
[32m+[m[32m* mailing state: MA[m
[32m+[m[32m* mailing zip: 02324[m
[32m+[m[32m* list date: 05-10-2025[m
[32m+[m[32m* list price: 2300[m
[32m+[m[32m* days on market: 85[m
[32m+[m[32m* lead date: 05-18-2025[m
[32m+[m[32m* status date: 08-03-2025[m
[32m+[m[32m* listing agent: Matthew Andrade[m
[32m+[m[32m* listing broker: Equity Management Realty, LLC[m
[32m+[m[32m* mls/fsbo id: 73372656[m
[32m+[m[32m* type: CI[m
[32m+[m[32m* year built: 1970[m
[32m+[m[32m* remarks: Long standing location of Bridgewater Veterinary clinic. Space is comprised currently of 2 units approximately 1900 Sqft. Located facing busy Rt18 with parking and signage in front of the building. Handy cap accessible front ramp, multiple exam rooms with working faucets throughout. Plenty of uses and visibility for someone looking to run a business in Bridgewater. Space would be split if desired. Tenant responsible for gas and electric. Space could be available for beginning of June.[m
[32m+[m[32m* phone counter: 0[m
[32m+[m[32m* email counter: 0[m
[32m+[m[32m* mail counter: 0[m
[32m+[m[32m* house number: 481[m
[32m+[m[32m* picture url: http://h3s.mlspin.com/photo/photo.aspx?h=200&w=256&mls=73372656&o=&n=0[m
[32m+[m[32m* tax id: BRIDM062L006"[m
[32m+[m[32mDhionys,Sampaio,New Lead,Seller,yes,yes,yes,,7817715212,52 Kingstown Way,"Duxbury, Ma",MA,02332,"[Vortex Source: Daily Expireds][m
[32m+[m
[32m+[m[32m* vortex id: 5e7e5b125f8c1277b80c8aef[m
[32m+[m[32m* lead status: New[m
[32m+[m[32m* listing status: Expired[m
[32m+[m[32m* property address: 52 Kingstown Way[m
[32m+[m[32m* property city: Duxbury, Ma[m
[32m+[m[32m* property state: MA[m
[32m+[m[32m* property zip: 02332[m
[32m+[m[32m* name: Dhionys Sampaio[m
[32m+[m[32m* name 2: Genainna Torres[m
[32m+[m[32m* mls name: Usa Va[m
[32m+[m[32m* phone: 781-771-5212[m
[32m+[m[32m* phone status: DNC[m
[32m+[m[32m* phone 2: 508-654-2535[m
[32m+[m[32m* phone 3: 781-582-1159[m