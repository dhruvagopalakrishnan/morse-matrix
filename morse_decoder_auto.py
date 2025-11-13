import cv2
import numpy as np
import time

# --- CRITICAL TIMING CALIBRATION ---
# These values are tuned to be slightly LESS than the Arduino's timings
# Arduino: Dot=0.2, Dash=0.6, LetterGap=0.6, WordGap=1.4

DOT_MAX_DURATION = 0.4      # Anything < 0.4s is a DOT
LETTER_GAP_MIN = 0.42       # If LED off for > 0.45s, LETTER FINISHED
WORD_GAP_MIN = 1.0          # If LED off for > 1.0s, WORD FINISHED (Space)

# -----------------------------------

# Morse Dictionary
MORSE_REV = { 
    '.-':'A', '-...':'B', '-.-.':'C', '-..':'D', '.':'E', '..-.':'F', '--.':'G', 
    '....':'H', '..':'I', '.---':'J', '-.-':'K', '.-..':'L', '--':'M', '-.':'N', 
    '---':'O', '.--.':'P', '--.-':'Q', '.-.':'R', '...':'S', '-':'T', '..-':'U', 
    '...-':'V', '.--':'W', '-..-':'X', '-.--':'Y', '--..':'Z', 
    '-----':'0', '.----':'1', '..---':'2', '...--':'3', '....-':'4', 
    '.....':'5', '-....':'6', '--...':'7', '---..':'8', '----.':'9'
}

# Color Calibration (Replace with your tuned numbers if using color mode)
# Defaulting to a broad Red/Orange range for typical LEDs
LOWER_COLOR = np.array([116,172,163]) 
UPPER_COLOR = np.array([179,255,255])

def main():
    cap = cv2.VideoCapture(0)
    
    # Variables for Logic
    led_is_on = False
    last_edge_time = time.time()
    
    current_symbol = ""      # Buffer: ".-"
    decoded_message = ""     # Final Text: "HI"
    
    # Flags to ensure we process gaps only once
    letter_processed = False 
    word_processed = False

    print("✅ Receiver Running. Waiting for Signal...")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        height, width = frame.shape[:2]
        
        # 1. DETECTION (HSV Color Method)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        
        # Find contours (blobs)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        is_signal_active = False
        if len(contours) > 0:
            # Get largest blob
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 50: # Filter tiny noise
                is_signal_active = True
                (x, y), radius = cv2.minEnclosingCircle(c)
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)

        # 2. TIMING & DECODING LOGIC
        current_time = time.time()
        duration = current_time - last_edge_time
        
        if is_signal_active:
            # --- LED IS ON ---
            if not led_is_on:
                # JUST TURNED ON
                led_is_on = True
                last_edge_time = current_time
                
                # Reset gap flags because a new signal started
                letter_processed = False
                word_processed = False
            
            status_text = "RECEIVING..."
            status_color = (0, 255, 0) # Green

        else:
            # --- LED IS OFF ---
            if led_is_on:
                # JUST TURNED OFF (Signal Ended)
                led_is_on = False
                last_edge_time = current_time
                
                # Determine if Dot or Dash
                if duration < DOT_MAX_DURATION:
                    current_symbol += "."
                else:
                    current_symbol += "-"
            
            else:
                # CONTINUOUSLY OFF (Waiting for Gap Thresholds)
                
                # Check for Letter Gap
                if duration > LETTER_GAP_MIN and not letter_processed and current_symbol != "":
                    if current_symbol in MORSE_REV:
                        decoded_char = MORSE_REV[current_symbol]
                        decoded_message += decoded_char
                        print(f"Parsed: {current_symbol} -> {decoded_char}") # Terminal Debug
                    else:
                        decoded_message += "?"
                    
                    current_symbol = "" # Clear the buffer for the next letter
                    letter_processed = True # Mark done so we don't add it again
                
                # Check for Word Gap
                if duration > WORD_GAP_MIN and not word_processed and len(decoded_message) > 0:
                    if decoded_message[-1] != " ": 
                        decoded_message += " "
                        print("Parsed: SPACE") # Terminal Debug
                    word_processed = True

            status_text = f"WAITING ({duration:.2f}s)"
            status_color = (0, 0, 255) # Red

        # 3. USER INTERFACE
        
        # Top Info Bar
        cv2.putText(frame, f"Symbol: {current_symbol}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, status_text, (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Bottom Message Bar (Black Box)
        cv2.rectangle(frame, (0, height - 80), (width, height), (0, 0, 0), -1)
        cv2.putText(frame, decoded_message, (20, height - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        cv2.imshow("Decoder", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('c'): decoded_message = ""

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()