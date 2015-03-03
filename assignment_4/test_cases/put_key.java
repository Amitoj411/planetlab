/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javaapplication7;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;

/**
 *
 * @author Owner
 */
public class JavaApplication7 {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws SocketException, IOException {
        // TODO code application logic here
//        String ADDR = "142.103.2.1";
        String ADDR = "127.0.0.1";
        int PORT = 50000;
        DatagramSocket sock = new DatagramSocket();
//        byte[] buf = new byte[64];
        byte[] buf;
//        buf[16] = 1; // Remove empty key
        buf=hexStringToByteArray("0700000000000000000000000000070701070000000000000000000000000000000000000000000000000000000000060603000F0F0F"); //
        DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
        sock.send(pack);
        sock.receive(pack);
        System.out.println(buf[16]);  // Should be 1, non-existent
        sock.close();
    }
    
    public static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                                 + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }
    
}
