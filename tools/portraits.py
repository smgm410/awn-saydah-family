# Portrait crops approved by Sarah on 14 and 16 Nov 2026 (Doc, box 11 crop bullets and Change log). Labels in the site's plain words:
# 'rec' = from the record; 'prob' = probably; 'fam' = the family says. Every person shown has died.
# Held back (no page chosen yet): the Saydah daughters crop from photo B (it opens the same full print as the Antoon and Wassela crops, so it was removed from both pages 17 Nov). Also held back, no person page yet: Joseph A. Awn (Home Reporter 1964), Helen Merhige (1923 passport application). Najeeb Zrake is not on the approved list.
ARTR = ' (our translation, to be confirmed by a native reader)'
LBL = {'rec': 'From the record.', 'page': 'From the page.' , 'prob': 'Probably him: ', 'fam': 'The family says.'}
P = []
def add(f, slugs, cap, label, who=''):
    P.append(dict(file=f, slugs=slugs.split(), cap=cap, label=label))
add('portrait_George-Aoun_1930_Ash-Shams-p104.jpg', 'george', 'George Aoun: printed portrait with its caption, Ash-Shams, 1 October 1930, p.104' + ARTR + '.', 'From the page.')
add('portrait_Khaleel-Saydah_1948_Miraat-al-Gharb-p4.jpg', 'khaleel', 'Khaleel Saydah: the photograph above the line we read as "the late Khalil Sayda", Mira’at al-Gharb, 3 December 1948, p.4' + ARTR + '.', 'From the page.')
add('portrait_Khaleel-W-Saydah_1920_passport-file-description.jpg', 'khaleel', 'Khaleel W. Saydah: photograph in his 1920 passport file.', 'From the record.')
add('portrait_Anthony-Awn_1939_declaration-of-intention.jpg', 'anthony', 'Anthony Aoun (Awn): photograph on his declaration of intention, 4 May 1939, with his signature "Anthony Aoun" beneath.', 'From the record.')
add('portrait_Anthony-Awn_1955_Caravan-p1.jpg', 'anthony', 'Anthony Awn: Caravan, 10 November 1955, p.1, caption "Anthony Awn" under "President of St. Nick’s".', 'The caption names him; probably our Anthony.')
add('portrait_John-Joseph-Awn_1940_declaration-of-intention.jpg', 'john', 'John J. Awn: photograph on his declaration of intention, 1940, with his signature "John J. Awn" beneath.', 'From the record.')
add('portrait_Mitchell-Awn_1939_declaration-of-intention.jpg', 'mitchell', 'Mitchell Awn: photograph on his declaration of intention, 15 November 1939, with his signature "Mitchell Joseph Khoury Aoun" beneath.', 'From the record.')
add('portrait_Mitchell-Awn_1955_Caravan-p1-honored.jpg', 'mitchell', 'Mitchell Awn: Caravan, 24 March 1955, p.1, "To be honored", caption "MITCHELL AWN, above".', 'The caption names him; probably our Mitchell.')
add('portrait_Elias-Awn_1937_declaration-of-intention.jpg', 'elias', 'Elias (Louis) Awn: photograph on his declaration of intention, 1937. The signature is partly covered by a printed note; we read it as "Elias Joseph Khoury Aoun".', 'From the record.')
add('portrait_Helen-Saydah_undated_family-photo-A.jpg', 'helen', 'Helen: family photograph A, undated.', 'The family says (the name is the family’s label on the print).')
add('portrait_Helen-Awn-with-infant-Joseph_undated_family-photo-C.jpg', 'helen', 'Helen with her infant son Joseph: family photograph C, undated.', 'The family says (the names are the family’s labels on the print).')
add('portrait_Anthony-and-Helen-Awn_undated_wedding-family-photo-D.jpg', 'anthony helen', 'Anthony and Helen: their wedding portrait. The print has no date.', 'The family says (the names are the family’s labels on the print).')
add('portrait_Antoon-Saydah_undated_family-photo-B.jpg', 'antoon', 'Antoon: from family photograph B (Anton, Wassela and three daughters), undated.', 'The family says (the names are the family’s labels on the print).')
add('portrait_Antoon-W-Saydah_1923_passport-application-image0851.jpg', 'antoon', 'Antoon W. Saydah: photograph on his 1923 passport application.', 'From the record.')
add('portrait_Wassela-Hadad_undated_family-photo-B.jpg', 'wassela', 'Wassela: from family photograph B (Anton, Wassela and three daughters), undated.', 'The family says (the names are the family’s labels on the print).')
add('portrait_Wassela-Hadad_undated_Jackie-Merhige-photo-15-004b.jpg', 'wassela', 'Wassela as a young woman: a studio print emailed by Jackie Merhige on 14 November 2026, undated.', 'The family says, in Jackie’s words; not a record.')
add('portrait_Saydah-daughters_undated_family-photo-B.jpg', '', 'The three daughters of Antoon and Wassela, from family photograph B, undated. The print carries no names, so we do not say which girl is which.', 'The family says.')
add('portrait_Evelyn-Saydah_1938_Bay-Ridge-yearbook-p98.jpg', 'evelyn', 'Evelyn Saydah: Bay Ridge High School yearbook "Maroon and White", 1938, p.98, the left photograph of the row that begins with her name.', 'Probably her: the photographs sit between two columns of names and are paired with the names by row.')
for f, cap in (
  ('portrait_Michael-W-Saydah_1915_passport-transcript-7-image658.jpg', 'Michael W. Saydah: photograph with his 1915 passport application (FamilySearch image 658), dated Chicago, 30 November 1915.'),
  ('portrait_Michael-W-Saydah_1919_passport-application-image0317.jpg', 'Michael W. Saydah: photograph on his 1919 passport application (Ancestry copy).'),
  ('portrait_Michael-W-Saydah_1919_passport-transcript-9-image318.jpg', 'Michael W. Saydah: the same 1919 application and photograph, the FamilySearch copy (image 318).'),
  ('portrait_Michael-W-Saydah_1922_passport-application-image0531.jpg', 'Michael W. Saydah: photograph on his 1922 passport application.')):
    add(f, 'michael-saydah', cap, 'From the record. Our identification of the sitter also rests on the family’s word.')
add('portrait_Michael-W-Saydah_undated_passport-transcript-5-image486.jpg', 'michael-saydah', 'Michael W. Saydah: photograph on an undated passport page (FamilySearch image 486); a handwritten name above it reads as "Michael W. Saydah".', 'Probably him; the name sits beside the photograph, and our identification also rests on the family’s word.')
add('portrait_Harold-M-Saydah_1921_passport-application-image0443.jpg', 'murad', 'Harold M. Saydah, Murad’s son: photograph on his 1921 passport application.', 'From the record.')
add('portrait_Ferris-M-Saydah_1923_passport-transcript-11-image553.jpg', 'murad', 'Ferris M. Saydah, Murad’s son: photograph on his 1923 passport application (FamilySearch image 553); the signature across the foot reads as his, in our reading.', 'From the record. Our identification also rests on the family’s word.')
add('portrait_Fred-Gorayeb_1921_passport-application-image158.jpg', 'fred-gorayeb', 'Fred Gorayeb: photograph on his 1921 passport application (FamilySearch image 158), with "Fred Naleem Gorayeb" signed beneath.', 'From the record.')

# Family photographs: the person page shows the close crop; the viewer opens the whole print.
FULL = {
 'portrait_Helen-Saydah_undated_family-photo-A.jpg': 'full_family-photo-A.jpg',
 'portrait_Helen-Awn-with-infant-Joseph_undated_family-photo-C.jpg': 'full_family-photo-C.jpg',
 'portrait_Anthony-and-Helen-Awn_undated_wedding-family-photo-D.jpg': 'full_family-photo-D.jpg',
 'portrait_Antoon-Saydah_undated_family-photo-B.jpg': 'full_family-photo-B.jpg',
 'portrait_Wassela-Hadad_undated_family-photo-B.jpg': 'full_family-photo-B.jpg',
 'portrait_Saydah-daughters_undated_family-photo-B.jpg': 'full_family-photo-B.jpg',
 'portrait_Wassela-Hadad_undated_Jackie-Merhige-photo-15-004b.jpg': 'full_Jackie-Merhige-photo-15-004b.jpg',
}
