# Eye_Blink_Based_MorseCode_Detection
**This project detects the blinks of a human eye, and used interpret the morse code into their natural language. **

 STEP 1: We use Dlibs Facial landmark technique to target the eyes in the face,that is marked with a coloured region.
 STEP 2: We use Eye Aspect Ratio (EAR) to calculate the blink, if it is greater than 0.5 we cnsider it as a blink and no blink if it is            less than 0.5.
 STEP 3: Classify the blink into short or long, based on the duration of blink by specifying the threshold value.
 STEP 4: Save this blinks into keyboard.
 STEP 5: Translate this morse code into natural language.
