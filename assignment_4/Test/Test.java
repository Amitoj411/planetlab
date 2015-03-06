package javaapplication7;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;

/**
 * EECE 411 Assignment 4
 * Java Test Cases
 * Tests check for correctness and performance.
 * 
 */
public class JavaApplication7 {

	final int PORT = 50000;
	
	final static String Node1 = "142.103.2.1";
	final static String Node2 = "142.103.2.2";
	final static String Node3 = "193.167.187.185";

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws SocketException, IOException {
    	//Test cases
    	testRemoteCommands();
    	//testCorrectRouting();
    	//testLoadBalancing();
    }
    
    public static void testRemoteCommands() throws SocketException, IOException {
      String ADDR = "127.0.0.1";
      int PORT = 50000;
      DatagramSocket sock = new DatagramSocket();
      byte[] buf;
      buf=hexStringToByteArray("0700000000000000000000000000070701070000000000000000000000000000000000000000000000000000000000060603000F0F0F");
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      System.out.println(buf[16]);
      sock.close();
    }
    
    public static void testCorrectRouting() throws SocketException, IOException {
//      String ADDR = "142.103.2.1";
      String ADDR = "127.0.0.1";
      int PORT = 50000;
      DatagramSocket sock = new DatagramSocket();
//      byte[] buf = new byte[64];
      byte[] buf;
//      buf[16] = 1; // Remove empty key
      buf=hexStringToByteArray("0700000000000000000000000000070701070000000000000000000000000000000000000000000000000000000000060603000F0F0F"); //
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      System.out.println(buf[16]);  // Should be 1, non-existent
      sock.close();
    }
    
    public static void testLoadBalancing() throws SocketException, IOException {
//      String ADDR = "142.103.2.1";
      String ADDR = "127.0.0.1";
      int PORT = 50000;
      DatagramSocket sock = new DatagramSocket();
//      byte[] buf = new byte[64];
      byte[] buf;
//      buf[16] = 1; // Remove empty key
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
