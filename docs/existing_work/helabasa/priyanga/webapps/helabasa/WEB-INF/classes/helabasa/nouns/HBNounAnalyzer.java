 / * *  
   *   @ a u t h o r   R a j i t h   P r i y a n g a   ( c )   2 0 1 3   -   r p r i y a n g a @ y a h o o . c o m    
   *    
   *    
   * /  
 p a c k a g e   h e l a b a s a . n o u n s ;  
  
 i m p o r t   h e l a b a s a . H B F o r m ;  
 i m p o r t   h e l a b a s a . H B K n o w l e d g e B a s e ;  
 i m p o r t   h e l a b a s a . H B L e m m a ;  
 i m p o r t   h e l a b a s a . H B P O S ;  
 i m p o r t   h e l a b a s a . H B S u f f i x S e t ;  
 i m p o r t   h e l a b a s a . H B T r a n s f o r m ;  
 i m p o r t   h e l a b a s a . H B T r a n s f o r m R u l e ;  
 i m p o r t   h e l a b a s a . H B T r a n s f o r m R u l e S e t ;  
 i m p o r t   h e l a b a s a . H B W o r d ;  
 i m p o r t   h e l a b a s a . H e l a b a s a ;  
 i m p o r t   h e l a b a s a . n o u n s . s c o r i n g . H B A v a i l a b i l i t y B a s e d S c o r i n g A l g o r i t h m ;  
 i m p o r t   h e l a b a s a . n o u n s . s c o r i n g . H B N o u n S c o r i n g A l g o r i t h m ;  
 i m p o r t   h e l a b a s a . s a n d h i . H B J o i n R e s u l t s S e t ;  
 i m p o r t   h e l a b a s a . s a n d h i . H B W o r d J o i n e r ;  
 i m p o r t   h e l a b a s a . s a n d h i . s c o r i n g . H B J o i n S c o r i n g A l g o r i t h m ;  
 i m p o r t   h e l a b a s a . s a n d h i . s c o r i n g . H B N o u n F o r m S c o r i n g A l o g o r i t h m ;  
  
 i m p o r t   j a v a . u t i l . A r r a y L i s t ;  
 i m p o r t   j a v a . u t i l . L i s t ;  
  
 p u b l i c   c l a s s   H B N o u n A n a l y z e r   {  
  
 	 L i s t < H B T r a n s f o r m R u l e S e t >   l i s t _ R u l e S e t   =   n e w   A r r a y L i s t < H B T r a n s f o r m R u l e S e t > ( ) ;  
 	  
 	 p u b l i c   H B N o u n A n a l y z e r ( )    
 	 { 	  
 	 }  
 	  
  
 	 / * *  
 	   *    
 	   *   @ p a r a m   s W o r d  
 	   *   @ r e t u r n  
 	   *    
 	   *   1 .   L o o k   u p   i n   t h e   K n o w l e d g e   B a s e  
 	   *   2 .   I f   n o   m a t c h e s ,   d i s j o i n   a l l   t h e   n o u n   s u f f i x e s  
 	   *   3 .   F o r   a l l   t h e   p o s s i b l e   l e m m a s ,   c o n j u g a t e   a s   N o u n s  
 	   *   4 .   E v a l u a t e   u s i n g   a   n o u n   s c o r i n g   a l g o r i t h m  
 	   *   5 .   F i n d   t h e   b e s t   M a t c h  
 	   * /  
 	 p u b l i c   s t a t i c   H B N o u n   A n a l y z e ( S t r i n g   s W o r d ,   H B N o u n C o n j u g a t i o n R u l e s   o C o n j u g a t i o n R u l e s ,   H B N o u n S c o r i n g A l g o r i t h m   o N o u n A l g o ,   H B J o i n S c o r i n g A l g o r i t h m   o J o i n A l g o )  
 	 { 	 	 	  
 	 	 L i s t < H B N o u n >   l i s t N o u n s   =   A n a l y z e ( s W o r d ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ) ;  
 	 	  
 	 	 i f ( l i s t N o u n s = = n u l l   | |   l i s t N o u n s . s i z e ( ) = = 0 )  
 	 	 {  
 	 	 	 r e t u r n   n u l l ;  
 	 	 }  
 	 	  
 	 	 i n t   i N o u n C o u n t   =   l i s t N o u n s . s i z e ( ) ;  
 	 	 i n t   i B e s t M a t c h   =   0 ;  
 	 	 l o n g   l M a x S c o r e   =   0 ;  
 	 	 f o r ( i n t   i = 0 ;   i < i N o u n C o u n t ;   i + + )  
 	 	 {  
 	 	 	 H B N o u n   o N o u n   =   l i s t N o u n s . g e t ( i ) ;  
 	 	 	 o N o u n A l g o . E v a l u a t e ( o N o u n ) ;  
 	 	 	  
 	 	 	 i f ( o N o u n . G e t S c o r e ( )   >   l M a x S c o r e )  
 	 	 	 {  
 	 	 	 	 i B e s t M a t c h   =   i ;  
 	 	 	 	 l M a x S c o r e   =   o N o u n . G e t S c o r e ( ) ;    
 	 	 	 }  
 	 	 }  
 	 	 	 	 	 	  
 	 	 r e t u r n   l i s t N o u n s . g e t ( i B e s t M a t c h ) ;  
 	 }  
  
 	 / * *  
 	   *    
 	   *   @ p a r a m   s W o r d  
 	   *   @ r e t u r n  
 	   *    
 	   *   1 .   L o o k   u p   i n   t h e   K n o w l e d g e   B a s e  
 	   *   2 .   I f   n o   m a t c h e s ,   d i s j o i n   a l l   t h e   n o u n   s u f f i x e s  
 	   *   3 .   F o r   a l l   t h e   p o s s i b l e   l e m m a s ,   c o n j u g a t e   a s   N o u n s    
 	   * /  
 	 p u b l i c   s t a t i c   L i s t < H B N o u n >   A n a l y z e ( S t r i n g   s W o r d ,   H B N o u n C o n j u g a t i o n R u l e s   o C o n j u g a t i o n R u l e s ,   H B J o i n S c o r i n g A l g o r i t h m   o J o i n A l g o )  
 	 { 	  
 	 	 H B W o r d   o W o r d   =   n e w   H B W o r d ( s W o r d ) ;  
 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : A n a l y z e :   [ "   +   s W o r d   +   " ] = "   +   o W o r d . G e t B a s e F o r m ( ) ) ;  
 	 	  
 	 	 H B L e m m a   o L e m m a     =   H B K n o w l e d g e B a s e . S e a r c h L e m m a ( s W o r d ) ;  
 	 	 i f ( o L e m m a ! = n u l l )  
 	 	 {  
 	 	 	 L i s t < H B N o u n >   l i s t N o u n s   =   G e t N o u n L i s t ( o L e m m a . G e t L e m m a W o r d ( ) ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ) ;  
 	 	 	 i f ( l i s t N o u n s ! = n u l l )  
 	 	 	 {  
 	 	 	 	 r e t u r n   l i s t N o u n s ;  
 	 	 	 }  
 	 	 }  
 	 	  
 	 	 H B F o r m   o F o r m   =   H B K n o w l e d g e B a s e . S e a r c h E x c e p t i o n ( s W o r d ) ;  
 	 	 i f ( o F o r m ! = n u l l   & &   o F o r m . G e t L e m m a ( ) ! = n u l l )  
 	 	 {  
 	 	 	 L i s t < H B N o u n >   l i s t N o u n s   =   G e t N o u n L i s t ( o F o r m . G e t L e m m a ( ) . G e t L e m m a W o r d ( ) ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ) ;  
 	 	 	 i f ( l i s t N o u n s ! = n u l l )  
 	 	 	 {  
 	 	 	 	 r e t u r n   l i s t N o u n s ;  
 	 	 	 }  
 	 	 } 	 	  
 	 	 	 	  
 	 	 L i s t < H B N o u n >   l i s t N o u n s   =   G e t N o u n L i s t ( o W o r d ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ) ;  
 	 	 r e t u r n   l i s t N o u n s ; 	 	 	 	  
 	 	  
 	 } 	  
  
 	  
 	 p r i v a t e   s t a t i c   L i s t < H B N o u n >   G e t N o u n L i s t ( H B W o r d   o W o r d ,   H B N o u n C o n j u g a t i o n R u l e s   o C o n j u g a t i o n R u l e s ,   H B J o i n S c o r i n g A l g o r i t h m   o J o i n A l g o )  
 	 {  
 	 	 L i s t < H B W o r d >   l i s t K R F o r m s   =   n e w   A r r a y L i s t < H B W o r d > ( ) ;  
 	 	 L i s t < H B N o u n >   l i s t N o u n s   =   n e w   A r r a y L i s t < H B N o u n > ( ) ;  
 	 	  
 	 	 H B S u f f i x S e t   o D e r i v e d R u l e S u f f i x e s   =   o C o n j u g a t i o n R u l e s . G e t D e r i v e d S u f f i x e s ( ) ;  
 	 	 H B S u f f i x S e t   o B a s e R u l e S u f f i x e s   =   o C o n j u g a t i o n R u l e s . G e t B a s e S u f f i x e s ( ) ;  
 	 	  
 	 	 G e t S t e m L i s t ( o W o r d ,   o D e r i v e d R u l e S u f f i x e s ,   l i s t K R F o r m s ) ;  
 	 	  
 	 	 i n t   i K R F o r m C o u n t   =   l i s t K R F o r m s . s i z e ( ) ;  
 	 	  
 	 	 H e l a b a s a . G e t L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : G e t N o u n L i s t   :   K R F o r m s = "   +   i K R F o r m C o u n t ) ;  
 	 	  
 	 	 i f ( i K R F o r m C o u n t   >   0 )  
 	 	 {  
 	 	 	 f o r ( i n t   i = 0 ;   i < i K R F o r m C o u n t ;   i + + )  
 	 	 	 {  
 	 	 	 	 H B W o r d   o K R F o r m   =   l i s t K R F o r m s . g e t ( i ) ;  
 	 	 	 	 G e t N o u n L i s t ( o K R F o r m ,   o B a s e R u l e S u f f i x e s ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s ) ;  
 	 	 	 } 	 	 	 	 	 	  
 	 	 }  
 	 	  
 	 	 i f ( l i s t N o u n s . s i z e ( ) = = 0 )  
 	 	 {  
 	 	 	 G e t N o u n L i s t ( o W o r d ,   o B a s e R u l e S u f f i x e s ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s ) ;  
 	 	 	 H e l a b a s a . G e t L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : G e t N o u n L i s t   :   N o   M a t c h e s   f o r   t h e   K R   f o r m s   s u f f i x e s " ) ; 	 	 	  
 	 	 }  
 	 	 e l s e  
 	 	 {  
 	 	 	 H e l a b a s a . G e t L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : G e t N o u n L i s t   :   N o u n s   f r o m   K R   F o r m s   :   "   +   l i s t N o u n s . s i z e ( ) ) ;  
 	 	 }  
 	  
 	 	 i f ( l i s t N o u n s . s i z e ( ) = = 0 )  
 	 	 {  
 	 	 	 G e t N o u n L i s t ( o W o r d ,   o B a s e R u l e S u f f i x e s ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s ) ;  
 	 	 	 H e l a b a s a . G e t L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : G e t N o u n L i s t   :   N o   M a t c h e s   f o r   g e n e r i c   s u f f i x e s " ) ; 	 	 	  
 	 	 }  
 	 	 e l s e  
 	 	 {  
 	 	 	 L i s t < H B W o r d >   l i s t L e m m a   =   n e w   A r r a y L i s t < H B W o r d > ( ) ;  
 	 	 	 l i s t L e m m a . a d d ( o W o r d ) ;  
 	 	 	 G e t N o u n L i s t ( l i s t L e m m a ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s ) ;  
 	 	 	 H e l a b a s a . G e t L o g ( ) . p r i n t l n ( " H B N o u n A n a l y z e r : : G e t N o u n L i s t   :   N o u n s   f o r   o r i g n a l   f o r m   :   "   +   l i s t N o u n s . s i z e ( ) ) ;  
 	 	 } 	 	  
 	 	  
 	 	 r e t u r n   l i s t N o u n s ;  
 	 }  
 	  
 	 p r i v a t e   s t a t i c   v o i d   G e t N o u n L i s t ( H B W o r d   o W o r d ,   H B S u f f i x S e t   o S u f f i x e s ,   H B N o u n C o n j u g a t i o n R u l e s   o C o n j u g a t i o n R u l e s ,   H B J o i n S c o r i n g A l g o r i t h m   o J o i n A l g o ,   L i s t < H B N o u n >   l i s t N o u n s )  
 	 { 	 	  
 	 	 L i s t < H B W o r d >   l i s t L e m m a s   =   n e w   A r r a y L i s t < H B W o r d > ( ) ;  
 	 	 L i s t < H B N o u n >   l i s t N o u n s 1   =   n e w   A r r a y L i s t < H B N o u n > ( ) ;  
 	 	  
 	 	 G e t S t e m L i s t B y S t e m m i n g ( o W o r d ,   o S u f f i x e s . G e t A p p e n d S u f f i x L i s t ( ) ,   l i s t L e m m a s ) ; 	 	  
 	 	 G e t N o u n L i s t ( l i s t L e m m a s ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s 1 ) ;  
 	 	  
 	 	 l i s t L e m m a s . c l e a r ( ) ;  
 	 	  
 	 	 i f ( l i s t N o u n s 1 . s i z e ( ) = = 0 )  
 	 	 {  
 	 	 	 G e t S t e m L i s t B y D i s j o i n i n g ( o W o r d ,   o S u f f i x e s . G e t J o i n S u f f i x L i s t ( ) ,   l i s t L e m m a s ) ;  
 	 	 	 G e t N o u n L i s t ( l i s t L e m m a s ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   l i s t N o u n s 1 ) ; 	  
 	 	 } 	  
 	  
 	 	 l i s t N o u n s . a d d A l l ( l i s t N o u n s 1 ) ;  
 	 } 	  
 	  
 	 p r i v a t e   s t a t i c   v o i d   G e t N o u n L i s t ( L i s t < H B W o r d >   l i s t L e m m a s ,   H B N o u n C o n j u g a t i o n R u l e s   o C o n j u g a t i o n R u l e s ,   H B J o i n S c o r i n g A l g o r i t h m   o J o i n A l g o ,   L i s t < H B N o u n >   l i s t N o u n s )  
 	 {  
 	 	 i n t   i L e m m a C o u n t   =   l i s t L e m m a s . s i z e ( ) ;  
 	 	  
 	 	 f o r ( i n t   i = 0 ;   i < i L e m m a C o u n t ;   i + + )  
 	 	 {  
 	 	 	 H B W o r d   o L e m m a   =   l i s t L e m m a s . g e t ( i ) ;  
 	 	 	 L i s t < H B N o u n >   l i s t L e m m a N o u n s   =   H B N o u n S y n t h e s i z e r . S y n t h e s i z e N o u n s ( o L e m m a ,   o C o n j u g a t i o n R u l e s ,   o J o i n A l g o ,   0 ) ;  
 	 	 	 i f ( l i s t L e m m a N o u n s ! = n u l l   & &   l i s t L e m m a N o u n s . s i z e ( ) > 0 )  
 	 	 	 {  
 	 	 	 	 l i s t N o u n s . a d d A l l ( l i s t L e m m a N o u n s ) ;  
 	 	 	 }  
 	 	 }  
 	 }  
 	  
 	 p r i v a t e   s t a t i c   v o i d   G e t S t e m L i s t ( H B W o r d   o W o r d ,   H B S u f f i x S e t   o S u f f i x e s ,   L i s t < H B W o r d >   l i s t S t e m s )  
 	 { 	 	  
 	 	 G e t S t e m L i s t B y S t e m m i n g ( o W o r d ,   o S u f f i x e s . G e t A p p e n d S u f f i x L i s t ( ) ,   l i s t S t e m s ) ;  
 	 	  
 	 	 i f ( l i s t S t e m s . s i z e ( ) = = 0 )  
 	 	 {  
 	 	 	 G e t S t e m L i s t B y D i s j o i n i n g ( o W o r d ,   o S u f f i x e s . G e t J o i n S u f f i x L i s t ( ) ,   l i s t S t e m s ) ;  
 	 	 } 	  
 	 }  
 	  
 	 p r i v a t e   s t a t i c   v o i d   G e t S t e m L i s t B y D i s j o i n i n g ( H B W o r d   o W o r d ,   L i s t < H B W o r d >   l i s t J o i n S u f f i x s ,   L i s t < H B W o r d >   l i s t S t e m s )  
 	 { 	  
 	 	 	 	 	 	  
 	 	 i n t   i J o i n S u f f i x C o u n t   =   l i s t J o i n S u f f i x s . s i z e ( ) ;  
 	 	 	 	  
 	 	 f o r ( i n t   i = 0 ;   i < i J o i n S u f f i x C o u n t ;   i + + )  
 	 	 {  
 	 	 	 H B W o r d   o S u f f i x   =   l i s t J o i n S u f f i x s . g e t ( i ) ; 	 	  
 	 	 	 	  
 	 	 	 H B J o i n R e s u l t s S e t   o R S   =   H B W o r d J o i n e r . D i s j o i n ( o W o r d ,   o S u f f i x ,   0 ) ;  
 	 	 	 i f ( o R S . G e t R e s u l t s C o u n t ( ) > 0 )  
 	 	 	 { 	  
 	 	 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " J o i n   M a t c h e s   f o r   "   +   o S u f f i x . G e t N a t u r a l F o r m ( )   +   "   :   "   +   o R S . G e t R e s u l t s C o u n t ( ) ) ;  
 	 	 	 	 f o r ( i n t   j = 0 ;   j < o R S . G e t R e s u l t s C o u n t ( ) ;   j + + )  
 	 	 	 	 {  
 	 	 	 	 	 H B W o r d   o S t e m   =   o R S . G e t R e s u l t s A t ( j ) . G e t R e s u l t ( ) ;  
 	 	 	 	 	  
 	 	 	 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " \ t L e m m a   :   "   +   o S t e m . G e t N a t u r a l F o r m ( )   +   "   :   J o i n   M e t h o d = "   +   o R S . G e t R e s u l t s A t ( j ) . G e t J o i n M e t h o d ( ) ) ;  
 	 	 	 	 	 l i s t S t e m s . a d d ( o S t e m ) ;  
 	 	 	 	 }  
 	 	 	 } 	 	 	 	  
 	 	 } 	 	  
 	 }  
 	  
 	 p r i v a t e   s t a t i c   v o i d   G e t S t e m L i s t B y S t e m m i n g ( H B W o r d   o W o r d ,   L i s t < H B W o r d >   l i s t A p p e n d S u f f i x s ,   L i s t < H B W o r d >   l i s t S t e m s )  
 	 { 	 	  
 	 	 i n t   i A p p e n d S u f f i x C o u n t   =   l i s t A p p e n d S u f f i x s . s i z e ( ) ;  
 	 	 	 	  
 	 	 f o r ( i n t   i = 0 ;   i < i A p p e n d S u f f i x C o u n t ;   i + + )  
 	 	 {  
 	 	 	 H B W o r d   o S u f f i x   =   l i s t A p p e n d S u f f i x s . g e t ( i ) ;  
 	 	 	  
 	 	 	 / / i n t   i W o r d E n d   =   o W o r d . G e t N a t u r a l C h a r a c t e r C o u n t ( ) ;  
 	 	 	 	 	 	  
 	 	 	 / / H B W o r d   o E n d   =   o W o r d . S u b W o r d ( i B a s e F o r m B e g i n ,   o W o r d . G e t N a t u r a l C h a r a c t e r C o u n t ( ) )  
 	 	 	 i f ( o W o r d . E n d s W i t h ( o S u f f i x ) )  
 	 	 	 {  
 	 	 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " A p p e n d   M a t c h   f o r   "   +   o S u f f i x . G e t N a t u r a l F o r m ( ) ) ;  
 	 	 	 	  
 	 	 	 	 i n t   i E n d   =   o W o r d . G e t N a t u r a l C h a r a c t e r C o u n t ( )   -   o S u f f i x . G e t N a t u r a l C h a r a c t e r C o u n t ( ) ;  
 	 	 	 	 	 	 	 	  
 	 	 	 	 S t r i n g   s S t e m   =   o W o r d . S u b N a t u r a l F o r m S t r i n g ( 0 ,   i E n d ) ;  
 	 	 	 	 H B W o r d   o S t e m   =   n e w   H B W o r d ( s S t e m ) ;  
 	 	 	 	  
 	 	 	 	 l i s t S t e m s . a d d ( o S t e m ) ;  
 	 	 	 	  
 	 	 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " \ t L e m m a   :   "   +   o S t e m . G e t N a t u r a l F o r m ( ) ) ;  
 	 	 	 }  
 	 	 	 e l s e  
 	 	 	 {  
 	 	 	 	 H e l a b a s a . G e t D e b u g L o g ( ) . p r i n t l n ( " I g n o r e   "   +   o S u f f i x . G e t N a t u r a l F o r m ( ) ) ;  
 	 	 	 }  
 	 	 } 	 	  
  
 	 }  
 }  
