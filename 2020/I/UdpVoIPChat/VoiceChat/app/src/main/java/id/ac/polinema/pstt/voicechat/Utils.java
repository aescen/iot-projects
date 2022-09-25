package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.zip.CRC32;

public class Utils {

    public static String getChecksum(String message, String algorithm) throws IOException, NoSuchAlgorithmException {
        try {
            //Creating the MessageDigest object
            MessageDigest md = MessageDigest.getInstance(algorithm);

            //Passing data to the created MessageDigest Object
            md.update(message.getBytes(StandardCharsets.UTF_8));

            //Compute the message digest
            byte[] digest = md.digest();

            //Converting the byte array to HexString format
            StringBuilder hexString = new StringBuilder();

            for (byte b : digest) {
                hexString.append(Integer.toHexString(0xFF & b));
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            //Log.e("Checksum NSAex:", algorithm);
        }
        return null;
    }

    public static String getCRC32(String message){
        CRC32 crc = new CRC32();
        crc.update(message.getBytes(StandardCharsets.UTF_8));
        String enc = Long.toHexString(crc.getValue());
        return enc;
    }
}
