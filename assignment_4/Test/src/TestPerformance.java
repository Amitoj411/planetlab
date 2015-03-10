
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.text.DecimalFormat;

public class TestPerformance {
	
	
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
	private static String ADDR;
    
	
	public void Setup()
	{
		ADDR = Localhost;
	}
	
	public static void main(String[] args) throws SocketException, IOException {
		testPut20Keys();
		measureGetThroughput();
		//testKillNodes();
    }
    
	
    public static void testPut20Keys() throws SocketException, IOException {
    	
    	final int numberRuns = 20;
    	
    	System.out.println("Adding 20 Keys...");
    	
    	for (int i=0; i<numberRuns; i++)
    	{	
    		DatagramSocket sock = new DatagramSocket();
    		byte[] buf = new byte[64];
    		
    		//Unique Request Header
    		buf[0] = 7;
    		buf[15] = 7;
    		
    		//Put Command
    		buf[16] = 1;
    		
    		//Key Generator
    		int randInt = i+1;
    		buf[17] = (byte)randInt;
    		
    		//Value Length
    		buf[49] = 6;
    		
    		//Value Generator
    		buf[51] = (byte)(3 * randInt);
    		buf[52] = (byte)(1 * randInt);
    		buf[53] = (byte)(4 * randInt);
    		buf[54] = (byte)(3 * randInt);
    		buf[55] = (byte)(2 * randInt);
    		buf[56] = (byte)(3 * randInt);
    		
    		DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
    		sock.send(pack);
            sock.receive(pack);
            sock.close();
            
            System.out.println("Now Adding Key: " + i);
    	}
    	System.out.println("Finished adding keys.\n");
    }
    
    public static void measureGetThroughput() throws SocketException, IOException {
    	final int numberRuns = 10;
    	final double NANOTOMILLI = 1000000;
    	double averageThroughput = 0;
    	
    	DecimalFormat decimalFormat = new DecimalFormat();
		decimalFormat.setMaximumFractionDigits(4);
		decimalFormat.setMinimumFractionDigits(4);
    	
    	System.out.println("Measuring Average Throughput...");
    	
    	for (int i=0; i<numberRuns; i++)
    	{	
    		DatagramSocket sock = new DatagramSocket();
    		byte[] buf = new byte[64];
    		
    		//Unique Request Header
    		buf[0] = 7;
    		buf[15] = 7;
    		
    		//Put Command
    		buf[16] = 2;
    		
    		//Key Generator
    		int randInt = i+1;
    		buf[17] = (byte)randInt;
    		
    		DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(ADDR), PORT);
    		
    		long startTime = System.nanoTime();
    		sock.send(pack);
            sock.receive(pack);
            sock.close();
            long estimatedTime = System.nanoTime() - startTime;
            
            System.out.println("Key retrieved. Duration: " + decimalFormat.format(estimatedTime/NANOTOMILLI) + " ms");
            averageThroughput += estimatedTime/NANOTOMILLI;
    	}
    	
    	averageThroughput /= numberRuns;
    	System.out.println("Average Throughput: " + decimalFormat.format(averageThroughput) + " ms\n");
    }
   
    public static void testKillNodes() throws SocketException, IOException {
    	final String node1 = "142.103.2.1";
    	final String node2 = "142.103.2.2";
    	
    	//Kill a node.
    	DatagramSocket sock = new DatagramSocket();
        byte[] buf = new byte[64];
        buf[16] = 4; // Shutdown node
        DatagramPacket pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(node1), PORT);
        sock.send(pack);
        sock.receive(pack);
        sock.close();
        
        //Put a new key.
        buf = new byte[64];
        buf[16] = 1; // Add new key
        pack = new DatagramPacket(buf, buf.length, InetAddress.getByName(node2), PORT);
        sock.send(pack);
        sock.receive(pack);
        sock.close();
    }
}
