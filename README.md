Email Information Extractor
===================================
This python program was built during my second year at university in my natural language processing
module. There were two mai areas to the assignment: entity tagging and an ontology.

Solution
---------------
**Entity tagging**

There were 6 entities in total that required tagging. This included the start time,
end time, speaker and location of the seminar. Also sentences and paragraphs needed to be tagged.
An overarching theme of the way I went about this task was the utilisation of the header of the
emails. The header often included well specified data about the seminar. This could be extracted
and tagged with the safety of knowing that it was correct information. For example, in the header
you might find the line: “Who:     Jane Doe”. This pattern of information was reliable in a lot of
situations. I used regexes to extract the times, speakers and locations from the header. This
technique worked extremely well for times and with varying success for the latter two. This was
because times only have a finite amount of variation in how they are displayed. For instance, two
examples might be “2pm” and “2:00 PM”. This makes regexes very powerful as with some careful
manipulation they can be used to consistently tag all forms. When it comes to names and locations
though, there are unpredictable variations their representation. For instance, names may be preceded
by a title, such as “Professor Jane Doe” or followed by a place of work e.g. “Jane Doe, Google”.
These variations were unpredictable enough for me to struggle to capture just the name of the person
and not extra information. This gave rise to some incorrect tags. The problem is similar when
attempting to tag the location. Variations I struggled to account for led to some unusual tags
being made. Typically, in the case of an unusual variation I would capture too much information
which made tagging instances of the speaker and location later in the email difficult. As far as
tagging of the body of the email, I decided to rely on what I had captured in the header to then
find cases later which matched. This meant that if, for instance, the speaker was not provided in
the header then I did not tag it in the body. I decided against attempting to tag when no information
was provided. Techniques such as named entity recognition came to mind, but I believed that as well
as potentially tagging correct information it would also likely tag incorrect items. This is because
there would be no way to discern whether a name was the speaker of the seminar or simply a person 
being talked about in the email. As a result, I decided to, as a worst case, under-generate tags
for speakers and locations as opposed to over-generating. This meant that I had only tagged items
that I was reasonably sure were correct which I think was a sensible heuristic.

For sentence tagging I decided to use the sent_tokenize() from NLTK. I decided to use this as it has
been trained on many European languages and so its detection of sentence ends through characters and
punctuation was very reliable. I used this instead of a regex because I felt a regex would have been
a naïve approach as sentences are often extremely varied. For paragraph tagging there were two main
steps involved. Firstly, as I read in the email, I would create a list in which lines not separated
by empty lines were grouped together. This can be thought of as the base structure of a paragraph; a
‘chuck’ of text. I then used a regex to check each ‘chunk’ to see if it contained three words, one
after another, and then a common sentence end: a full stop, question mark, or exclamation mark. This
was a lightweight method to check to see if the ‘chunks’ of text contained what was likely to be a
sentence. If it passed this test, then I tagged it as a paragraph. This process worked very well. In
an extremely high percentage of the emails, paragraphs were successfully tagged, with false positives
being tremendously rare.

After completing my tagging, I did some quantitative analysis. I calculated the precision, recall
and F measure of my tagged data in comparison to the gold standard tagged data. Precision compares
the true positives I classified to what I classified as a whole. My precision score was 0.702
(3 s.f.). Recall compares the true positives I classified to the true positives classified in the
gold standard. My recall score was 0.508 (3 s.f.). Finally, F measure combines precision and recall
giving a balancing score between the two. My F measure score was 0.573 (3 s.f.). I think these scores
are an accurate reflection of some of the methods I used.  For instance, my tagging of locations and
speakers focused on under generation. This is evident in my precision score being higher than
recall: What I was tagging was correct in a lot of cases, but I was not tagging all the instances
in the text. I believe recall could have been improved by being more aggressive in my tagging, but
this would have likely been at the cost of precision. 
 
**Ontology**

For the ontology I opted to combine a variety of NLP techniques to achieve my result. Upon
reading in an email, I word tokenized the whole text. I then proceeded to normalise the words using
lemmatization. I chose lemmatizing over stemming as in my opinion stemming can be overaggressive in
its shortening of words. Following this, I filtered out words which contained dots (as these were
likely abbreviations or nonsense) and restricted the words to those which were longer than 4 letters.
The latter step was to remove words such as “and”, “then” and “or” which were irrelevant to the task.
I then part-of-speech tagged the words and selected those which were nouns or plural nouns. Before
this I also made the text lowercase as the POS tagger tended to tag anything with a capital letter
(such as the title of the seminar) as a proper noun as opposed to a regular noun. I then used WordNet
to check if any of the words had definitions as anything other than a noun. For example, the word “run”
can be both a noun and a verb, so would be filtered out. “Science” on the other hand can only ever be
a noun. After this I filtered out words which were male, female or family names. Finally, I counted the
occurrences of each word in the text and ranked them. The top word became the category. The success of
this system varied quite a bit. It generated a lot of categories with some being more appropriate than
others. For instance, good categories included “robotics”, “vision” and “computer”. However some more
unusual categories included “problem”, “agent” and “grandillo”. That final category is an example of a
family name that was not part of the “names.family” file I had acquired. This is inevitable as no list
of names can ever be complete. This resulted in a dozen categories being names that were slightly
obscure and so weren’t filtered out at an earlier stage in the process. Although, the ontology method
I developed had varying success I believe its ability to be used on any email, or really any piece of
text, makes it useful as it is not restricted and in a lot of cases provides meaningful categorisation.
