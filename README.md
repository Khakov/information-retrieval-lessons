# information-retrieval-lessons
1. Parse site and create issues.xml
2. Create 2 text normilize porter stemmer and Mystem stemmer
3. Create inverter index for mystem/porter
4. Binary searching with term add `-` for exlude from search query
#
Example:
 - what is banana?
 - what is apple
 - apple
 
`what banana` return {1}, `what is` return {1,2}, `what is orange` return {}, `what -apple` return {1}
#
5. TF-IDF index for keyword words
6. create LSI (Latent semantic index)
