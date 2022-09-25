package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Enumeration;

public class IpUtils {
    private static InetAddress localIp = null;
    private static InetAddress bcIp = null;
    private static Boolean isWiFiAvailable;
    private static String LOG_TAG = "IpUtil:";

    public static boolean isWiFiAvailable() {
        String localIp;
        try{
            localIp = IpUtils.getLocalIpAddress().getHostAddress();
            isWiFiAvailable = true;
        }catch (NullPointerException e){
            isWiFiAvailable = false;
        }
        return isWiFiAvailable;
    }

    public static InetAddress getLocalIpAddress() {
        try {
            for (Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces(); en
                    .hasMoreElements();) {
                NetworkInterface intf = en.nextElement();
                if (intf.getName().contains("wlan")) {
                    for (Enumeration<InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr
                            .hasMoreElements();) {
                        InetAddress inetAddress = enumIpAddr.nextElement();
                        if (!inetAddress.isLoopbackAddress()
                                && (inetAddress.getAddress().length == 4)) {
                            ////Log.d(LOG_TAG, inetAddress.getHostAddress());
                            localIp = InetAddress.getByName(inetAddress.getHostAddress());
                            return localIp;
                        }
                    }
                }
            }
        } catch (SocketException | UnknownHostException ex) {
            //Log.e(LOG_TAG, ex.toString());
        }
        return localIp;
    }

    public static InetAddress getBroadcastIp() {

        //function to return the broadcast address, based on the IP address of the device
        try {
            String localIP = getLocalIpAddress().getHostAddress();
            String[] addrArray = localIP.split("\\.");
            bcIp = InetAddress.getByName(addrArray[0]+"."+addrArray[1]+"."+addrArray[2]+".255");
            //Log.i(LOG_TAG, "Broadcast IP: " + bcIp);
            return bcIp;

        }

        catch (UnknownHostException e) {

            //Log.e(LOG_TAG, "UnknownException in get BroadcastIP: " + e);
            return bcIp;

        }

    }
}
