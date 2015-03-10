
import static org.junit.Assert.*;
import org.junit.*;

import org.junit.runners.MethodSorters;
import org.junit.FixMethodOrder;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class TestCorrectness {
	
	
	//PlanetLab Testing
	/*
	final static String Node1 = "142.103.2.1";
	final static String Node2 = "142.103.2.2";
	final static String Node3 = "193.167.187.185";
	*/
	
	//Local Testing
	final static String Localhost = "localhost";
	
	//Other member variables
	final static int PORT = 50000;
	private String ADDR;
	
	@Before
	public void Setup()
	{
		ADDR = Localhost;
	}
	
	//Constant Enumerations
	public enum Response {
		SUCCESS(0x01), NONEXISTENTKEY(0x02), OUTOFSPACE(0x03), OVERLOAD(0x04), STOREFAILURE(0x05), UNRECOGNIZED(0x06);
		
	    private final int value;
	    Response(int value) { this.value = value; }
	    public int getValue() { return value; }
	};
    
    @Test
    public void testGetNonExistentKey() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = new byte[64];
      buf[16] = 2; // Get nonexistent key
      
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.NONEXISTENTKEY.getValue(), buf[16]);
      sock.close();
    }
	
    @Test
    public void testRemoveNonExistentKey() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = new byte[64];
      buf[16] = 3; // Remove nonexistent key
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.NONEXISTENTKEY.getValue(), buf[16]);
      sock.close();
    }
    
    @Test
    public void testUnrecognizedCommand() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = new byte[64];
      buf[16] = 7; // Nonexistent command
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.UNRECOGNIZED.getValue(), buf[16]);
      sock.close();
    }
    
    @Test
    public void testPutNewKey() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = hexStringToByteArray("0700000000000000000000000000070701070000000000000000000000000000000000000000000000000000000000060603000F0F0F");
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.SUCCESS.getValue(), buf[16]);
      sock.close();
    }
    
    @Test
    public void testGetExistingKey() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = hexStringToByteArray("030000000000000000000000000007070207000000000000000000000000000000000000000000000000000000000006060000000000");
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.SUCCESS.getValue(), buf[16]);
      sock.close();
    }
    
    @Test
    public void testRemoveExistingKey() throws SocketException, IOException {
      DatagramSocket sock = new DatagramSocket();
      byte[] buf = hexStringToByteArray("080000000000000000000000000007070307000000000000000000000000000000000000000000000000000000000006060000000000");
      DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
      sock.send(pack);
      sock.receive(pack);
      assertEquals(Response.SUCCESS.getValue(), buf[16]);
      sock.close();
    }
      
    @Test
    public void testShutdown() throws SocketException, IOException {
        DatagramSocket sock = new DatagramSocket();
        byte[] buf = new byte[64];
        buf[16] = 4; // Shutdown node
        DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
        sock.send(pack);
        sock.receive(pack);
        assertEquals(Response.SUCCESS.getValue(), buf[16]);
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
