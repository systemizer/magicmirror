//
//  MMViewController.m
//  MagicMirror
//
//  Created by Doug Feigelson on 7/21/12.
//  Copyright (c) 2012 MIT. All rights reserved.
//

#import "MMViewController.h"
#import <RestKit/RestKit.h>
#import <AVFoundation/AVFoundation.h>

#define DOCUMENTS_FOLDER [NSHomeDirectory() stringByAppendingPathComponent:@"Documents"]

int RECORDING_PERIOD = 10;
    
@interface MMViewController ()

@end

@implementation MMViewController
@synthesize recorder,webView;

- (void)viewDidLoad
{
    [super viewDidLoad];
    
    // Setup the webview
    webView = [[UIWebView alloc] initWithFrame:CGRectMake(0, 0, 1024, 768)];
    webView.delegate = self;
    [self.view addSubview:webView];
    
    AVAudioSession *audioSession = [AVAudioSession sharedInstance];
    NSError *err = nil;
    [audioSession setCategory :AVAudioSessionCategoryPlayAndRecord error:&err];
    if(err){
        NSLog(@"audioSession: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        return;
    }
    [audioSession setActive:YES error:&err];
    err = nil;
    if(err){
        NSLog(@"audioSession: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        return;
    }
    
    BOOL audioHWAvailable = audioSession.inputIsAvailable;
    if (! audioHWAvailable) {
        UIAlertView *cantRecordAlert =
        [[UIAlertView alloc] initWithTitle: @"Warning"
                                   message: @"Audio input hardware not available"
                                  delegate: nil
                         cancelButtonTitle:@"OK"
                         otherButtonTitles:nil];
        [cantRecordAlert show];
        return;
    }
    
    [self makeNewRecorderAndRecord];
}

-(void) makeNewRecorderAndRecord {
    NSDictionary *recordSettings = [NSDictionary dictionaryWithObjectsAndKeys:
                                    [NSNumber numberWithInt:AVAudioQualityMedium],AVEncoderAudioQualityKey,
                                    [NSNumber numberWithInt:16], AVEncoderBitRateKey,
                                    [NSNumber numberWithInt: 2], AVNumberOfChannelsKey,
                                    [NSNumber numberWithFloat:16000.0], AVSampleRateKey,
                                    nil];
    
    
    // Create a new dated file
    NSDate *now = [NSDate dateWithTimeIntervalSinceNow:0];
    NSString *caldate = [now description];
    recordingFilePath = [NSString stringWithFormat:@"%@/%@.caf", DOCUMENTS_FOLDER, caldate];
    NSURL *url = [NSURL fileURLWithPath:recordingFilePath];
    NSError* err = nil;
    recorder = [[ AVAudioRecorder alloc] initWithURL:url settings:recordSettings error:&err];
    if(!recorder){
        NSLog(@"recorder: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        UIAlertView *alert =
        [[UIAlertView alloc] initWithTitle: @"Warning"
                                   message: [err localizedDescription]
                                  delegate: nil
                         cancelButtonTitle:@"OK"
                         otherButtonTitles:nil];
        [alert show];
        return;
    }
    
    //prepare to record
    [recorder setDelegate:self];
    [recorder prepareToRecord];
//    recorder.meteringEnabled = YES;
    
    // start recording
    [recorder recordForDuration:(NSTimeInterval) RECORDING_PERIOD];
}


-(void) audioRecorderDidFinishRecording:(AVAudioRecorder *)recorder successfully:(BOOL)flag {
    NSLog(@"RECORDER DONE. SENDING AND RESTARTING!");
    NSURL *url = [NSURL fileURLWithPath: recordingFilePath];
    NSError *err = nil;
    NSData *audioData = [NSData dataWithContentsOfFile:[url path] options: 0 error:&err];
        
    RKObjectManager* om = [RKObjectManager sharedManager];
    NSLog(@"%@",om.baseURL);
    RKParams* params = [RKParams params];
    
    // submit audio file in post
    [params setData:audioData MIMEType:@"audio/x-wav" forParam:@"recording"];
    
    [params setValue:@"something" forParam:@"something"];
    [om.client post:@"/audio" params:params delegate:self];
    
    [self.recorder deleteRecording];
    [self makeNewRecorderAndRecord];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

-(void) request:(RKRequest *)request didFailLoadWithError:(NSError *)error {
    NSLog(@"%@",error.description);
}

-(void) request:(RKRequest *)request didLoadResponse:(RKResponse *)response {
    NSLog(@"RESPONSE LOADED: \n\n  %@",response.bodyAsString);


    CATransition *animation = [CATransition animation];
    [animation setDelegate:self];
    [animation setDuration:2.0f];
    animation.startProgress = 0;
    animation.endProgress   = 1; 
    [animation setTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
    [animation setType:@"crossfade"];
    [animation setSubtype:kCATransitionFade];
    
    [animation setRemovedOnCompletion:NO];
    //    [animation setFillMode: @"extended"];
    [[webView layer] addAnimation:animation forKey:@"crossfade"]; 

    [webView loadHTMLString:response.bodyAsString baseURL:[NSURL URLWithString:@"http://"]];

//    [webView removeFromSuperview];
//    //    [self.view addSubview:newWebView];
//    [webView loadHTMLString:response.bodyAsString baseURL:[NSURL URLWithString:@"http://"]];
//
    [UIView beginAnimations:@"crossfade" context:nil];
    [UIView setAnimationDuration:1.0];
    [UIView setAnimationCurve:UIViewAnimationCurveEaseInOut];
    [UIView commitAnimations];    
    
//    [self.view addSubview:newView];
//    [webView loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"http://en.wikipedia.org/wiki/Special:Random"]]];

}

-(void)webViewDidFinishLoad:(UIWebView *) newWebView {
    return;
    CATransition *animation = [CATransition animation];
    [animation setDelegate:self];
    [animation setDuration:2.0f];
    animation.startProgress = 0;
    animation.endProgress   = 1; 
    [animation setTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionLinear]];
    [animation setType:@"crossfade"];
    [animation setSubtype:kCATransitionFade];
    
    [animation setRemovedOnCompletion:NO];
//    [animation setFillMode: @"extended"];
    [[self.view layer] addAnimation:animation forKey:@"crossfade"]; 
    [webView removeFromSuperview];
//    [self.view addSubview:newWebView];
    
    [UIView beginAnimations:@"crossfade" context:nil];
    [UIView setAnimationDuration:1.0];
    [UIView setAnimationCurve:UIViewAnimationCurveEaseInOut];
    [UIView commitAnimations];    
}

@end
